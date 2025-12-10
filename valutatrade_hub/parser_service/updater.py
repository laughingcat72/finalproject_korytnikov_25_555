
import logging
from typing import Dict
from .config import ParserConfig
from .api_clients import CoinGeckoClient, ExchangeRateApiClient
from .storage import RatesStorage
from ..core.exceptions import ApiRequestError

logger = logging.getLogger("valutatrade")


class RatesUpdater:

    def __init__(self, config: ParserConfig = None):  # type: ignore
        self.config = config or ParserConfig()

        self.coingecko_client = CoinGeckoClient(self.config)
        self.exchangerate_client = ExchangeRateApiClient(self.config)

        self.storage = RatesStorage(
            self.config.RATES_FILE_PATH,
            self.config.HISTORY_FILE_PATH
        )

        logger.info("Инициализирован RatesUpdater")

    def run_update(self, source: str = None) -> Dict:  # type: ignore

        logger.info("=" * 50)
        logger.info("Начало обновления курсов валют")

        all_rates = {}
        errors = []

        try:

            if source in [None, "coingecko"]:
                try:
                    logger.info("Получение курсов криптовалют от CoinGecko...")
                    crypto_rates = self.coingecko_client.fetch_rates()
                    all_rates.update(crypto_rates)

                    self.storage.save_to_history(crypto_rates, "CoinGecko")
                    logger.info(
                        f"✓ Получено {len(crypto_rates)} крипто-курсов")

                except ApiRequestError as e:
                    error_msg = f"Ошибка CoinGecko: {e}"
                    logger.error(error_msg)
                    errors.append(error_msg)

            if source in [None, "exchangerate"]:
                try:
                    logger.info(
                        "Получение курсов фиатных валют от ExchangeRate-API...")
                    fiat_rates = self.exchangerate_client.fetch_rates()
                    all_rates.update(fiat_rates)

                    self.storage.save_to_history(
                        fiat_rates, "ExchangeRate-API")
                    logger.info(f"✓ Получено {len(fiat_rates)} фиатных курсов")

                except ApiRequestError as e:
                    error_msg = f"Ошибка ExchangeRate-API: {e}"
                    logger.error(error_msg)
                    errors.append(error_msg)

            if all_rates:

                if source == "coingecko":
                    save_source = "CoinGecko"
                elif source == "exchangerate":
                    save_source = "ExchangeRate-API"
                else:
                    save_source = "Mixed"

                success = self.storage.save_current_rates(
                    all_rates, save_source)
                if success:
                    logger.info(f"✓ Сохранено {len(all_rates)} курсов в кеш")
                else:
                    errors.append("Не удалось сохранить курсы в кеш")

            result = {
                "total_rates": len(all_rates),
                "updated_pairs": list(all_rates.keys()),
                "errors": errors,
                "success": len(errors) == 0
            }

            if errors:
                logger.warning(
                    f"Обновление завершено с ошибками. Обновлено: {len(all_rates)} курсов")
                for error in errors:
                    logger.warning(f"  - {error}")
            else:
                logger.info(
                    f"✓ Обновление успешно завершено. Обновлено: {len(all_rates)} курсов")

            logger.info("=" * 50)
            return result

        except Exception as e:
            logger.error(f"Критическая ошибка при обновлении курсов: {e}")
            raise

    def get_cache_info(self) -> Dict:

        data = self.storage.get_current_rates()
        pairs_count = len(data.get("pairs", {}))
        last_refresh = data.get("last_refresh", "Никогда")

        return {
            "pairs_count": pairs_count,
            "last_refresh": last_refresh,
            "is_expired": self.storage.is_cache_expired(self.config.REQUEST_TIMEOUT)
        }
