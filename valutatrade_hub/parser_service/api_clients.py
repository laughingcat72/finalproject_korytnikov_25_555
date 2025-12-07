import requests
import logging
from abc import ABC, abstractmethod
from typing import Dict
from ..core.exceptions import ApiRequestError
from .config import ParserConfig

logger = logging.getLogger("valutatrade")


class BaseApiClient(ABC):
    """Абстрактный базовый класс для API-клиентов"""

    @abstractmethod
    def fetch_rates(self) -> Dict[str, float]:
        """Получить курсы валют"""
        pass


class CoinGeckoClient(BaseApiClient):
    """Клиент для работы с CoinGecko API"""

    def __init__(self, config: ParserConfig):
        self.config = config
        self.base_url = config.COINGECKO_URL

    def fetch_rates(self) -> Dict[str, float]:
        """Получить курсы криптовалют"""
        try:
            crypto_ids = [self.config.CRYPTO_ID_MAP[code]
                          for code in self.config.CRYPTO_CURRENCIES]
            ids_param = ",".join(crypto_ids)

            params = {
                'ids': ids_param,
                'vs_currencies': 'usd'
            }

            logger.info("Запрос к CoinGecko")
            response = requests.get(
                self.base_url,
                params=params,
                timeout=self.config.REQUEST_TIMEOUT
            )

            if response.status_code != 200:
                raise ApiRequestError(
                    f"CoinGecko вернул статус {response.status_code}")

            data = response.json()
            rates = {}
            for crypto_code in self.config.CRYPTO_CURRENCIES:
                crypto_id = self.config.CRYPTO_ID_MAP[crypto_code]
                if crypto_id in data and 'usd' in data[crypto_id]:
                    rate = data[crypto_id]['usd']
                    pair_key = f"{crypto_code}_{self.config.BASE_CURRENCY}"
                    rates[pair_key] = rate
                    logger.debug(f"Получен курс {pair_key}: {rate}")

            logger.info(f"Получено {len(rates)} крипто-курсов от CoinGecko")
            return rates

        except requests.exceptions.RequestException as e:
            raise ApiRequestError(f"Ошибка сети при запросе к CoinGecko: {e}")
        except Exception as e:
            raise ApiRequestError(
                f"Ошибка при обработке ответа CoinGecko: {e}")


class ExchangeRateApiClient(BaseApiClient):
    """Клиент для работы с ExchangeRate-API"""

    def __init__(self, config: ParserConfig):
        self.config = config
        self.api_key = config.EXCHANGERATE_API_KEY

        if not self.api_key:
            self.api_key = "71ccd029b9f44cf21cdf6fe7"
            logger.warning("Используем хардкодный API ключ")

        self.base_url = f"https://v6.exchangerate-api.com/v6/{self.api_key}/latest/USD"

    def fetch_rates(self) -> Dict[str, float]:
        """Получить курсы фиатных валют"""
        try:
            logger.info("Запрос к ExchangeRate-API")

            response = requests.get(
                self.base_url,
                timeout=self.config.REQUEST_TIMEOUT
            )

            print(f"DEBUG: Status Code: {response.status_code}")

            if response.status_code != 200:
                raise ApiRequestError(
                    f"ExchangeRate-API вернул статус {response.status_code}")

            data = response.json()
            print(f"DEBUG: API result: {data.get('result')}")
            print(f"DEBUG: Base currency: {data.get('base_code')}")

            if data.get('result') != 'success':
                error_type = data.get('error-type', 'unknown')
                print(f"DEBUG: API Error type: {error_type}")
                raise ApiRequestError(f"API вернул ошибку: {error_type}")

            # ИСПРАВЛЕНИЕ: используем "conversion_rates" вместо "rates"
            rates_data = data.get('conversion_rates', {})

            # Выводим первые 5 валют для проверки
            available_currencies = list(rates_data.keys())
            print(f"DEBUG: Всего валют: {len(available_currencies)}")
            print(f"DEBUG: Первые 5: {available_currencies[:5]}")

            # Ищем нужные нам валюты
            rates = {}
            for fiat_code in self.config.FIAT_CURRENCIES:
                if fiat_code in rates_data:
                    # API возвращает: 1 USD = X EUR (например 0.8585)
                    # Нам нужно: 1 EUR = ? USD = 1 / 0.8585 = 1.164
                    rate_from_api = rates_data[fiat_code]
                    if rate_from_api > 0:
                        rate = 1 / rate_from_api
                        pair_key = f"{fiat_code}_USD"
                        rates[pair_key] = rate
                        print(
                            f"DEBUG: {pair_key}: 1 USD = {rate_from_api} {fiat_code}, значит 1 {fiat_code} = {rate:.4f} USD")
                        logger.debug(f"Получен курс {pair_key}: {rate}")
                else:
                    print(f"WARN: Валюта {fiat_code} отсутствует в ответе API")
                    logger.warning(f"Курс для {fiat_code} не найден в ответе")

            logger.info(
                f"Получено {len(rates)} фиатных курсов от ExchangeRate-API")
            return rates

        except requests.exceptions.RequestException as e:
            print(f"ERROR: Network error: {e}")
            raise ApiRequestError(f"Ошибка сети: {e}")
        except Exception as e:
            print(f"ERROR: Unexpected error: {e}")
            raise ApiRequestError(f"Ошибка обработки: {e}")
