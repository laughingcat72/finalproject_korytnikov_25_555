import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import logging

logger = logging.getLogger("valutatrade")


class RatesStorage:
    """Класс для работы с хранилищами курсов"""

    def __init__(self, rates_file_path: str, history_file_path: str):
        self.rates_file_path = Path(rates_file_path)
        self.history_file_path = Path(history_file_path)

        # Создаем директории если их нет
        self.rates_file_path.parent.mkdir(exist_ok=True, parents=True)
        self.history_file_path.parent.mkdir(exist_ok=True, parents=True)

    def save_current_rates(self, rates: Dict[str, float], source: str):
        """
        Сохраняет текущие курсы в rates.json (снимок текущего мира)
        Формат как в задании:
        {
          "pairs": {
            "EUR_USD": { "rate": 1.0786, "updated_at": "...", "source": "..." },
            "BTC_USD": { "rate": 59337.21, "updated_at": "...", "source": "..." }
          },
          "last_refresh": "..."
        }
        """
        try:
            timestamp = datetime.utcnow().isoformat() + "Z"

            # Создаем структуру данных
            pairs_data = {}
            for pair_key, rate in rates.items():
                pairs_data[pair_key] = {
                    "rate": rate,
                    "updated_at": timestamp,
                    "source": source
                }

            data = {
                "pairs": pairs_data,
                "last_refresh": timestamp
            }

            # Атомарная запись через временный файл
            temp_file = self.rates_file_path.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            # Переименовываем
            temp_file.replace(self.rates_file_path)

            logger.info(
                f"Сохранено {len(rates)} курсов в {self.rates_file_path}")
            return True

        except Exception as e:
            logger.error(f"Ошибка при сохранении текущих курсов: {e}")
            return False

    def save_to_history(self, rates: Dict[str, float], source: str):
        """
        Сохраняет курсы в exchange_rates.json (исторические данные)
        Формат как в задании:
        {
          "id": "BTC_USD_2025-10-10T12:00:00Z",
          "from_currency": "BTC",
          "to_currency": "USD",
          "rate": 59337.21,
          "timestamp": "2025-10-10T12:00:00Z",
          "source": "CoinGecko",
          "meta": { ... }
        }
        """
        try:
            timestamp = datetime.utcnow().isoformat() + "Z"

            # Читаем существующую историю или создаем новую
            history = self._load_history()

            # Добавляем новые записи
            for pair_key, rate in rates.items():
                # Разбираем пару валют
                from_currency, to_currency = pair_key.split('_')

                # Создаем уникальный ID как в задании
                record_id = f"{from_currency}_{to_currency}_{timestamp}"

                record = {
                    "id": record_id,
                    "from_currency": from_currency,
                    "to_currency": to_currency,
                    "rate": rate,
                    "timestamp": timestamp,
                    "source": source,
                    "meta": {
                        "request_ms": 0,  # Можно добавить реальное время
                        "status_code": 200
                    }
                }

                history.append(record)
                logger.debug(f"Добавлена историческая запись: {record_id}")

            # Сохраняем историю
            temp_file = self.history_file_path.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)

            temp_file.replace(self.history_file_path)

            logger.info(f"Добавлено {len(rates)} записей в историю")
            return True

        except Exception as e:
            logger.error(f"Ошибка при сохранении истории: {e}")
            return False

    def _load_history(self) -> List[dict]:
        """Загружает исторические данные из файла"""
        try:
            if self.history_file_path.exists():
                with open(self.history_file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.warning(f"Не удалось загрузить историю: {e}")
            return []

    def get_current_rates(self) -> Dict:
        """Возвращает текущие курсы из кеша"""
        try:
            if self.rates_file_path.exists():
                with open(self.rates_file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {"pairs": {}, "last_refresh": None}
        except Exception as e:
            logger.error(f"Ошибка при чтении текущих курсов: {e}")
            return {"pairs": {}, "last_refresh": None}

    def is_cache_expired(self, ttl_seconds: int) -> bool:
        """Проверяет устарел ли кеш"""
        data = self.get_current_rates()
        last_refresh = data.get("last_refresh")

        if not last_refresh:
            return True

        try:
            # Убираем 'Z' если есть и парсим
            last_refresh_clean = last_refresh.rstrip('Z')
            last_time = datetime.fromisoformat(last_refresh_clean)
            current_time = datetime.utcnow()

            # Оба времени теперь offset-naive
            age = (current_time - last_time).total_seconds()
            return age > ttl_seconds

        except Exception as e:
            logger.warning(f"Ошибка при проверке срока годности кеша: {e}")
            return True
