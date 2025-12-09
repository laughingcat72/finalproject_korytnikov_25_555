# valutatrade_hub/parser_service/config.py
import os
from dataclasses import dataclass, field
from typing import Dict, Tuple


@dataclass
class ParserConfig:
    # Ключ загружается из переменной окружения
    EXCHANGERATE_API_KEY: str = os.getenv("EXCHANGERATE_API_KEY", "")

    # Эндпоинты
    COINGECKO_URL: str = "https://api.coingecko.com/api/v3/simple/price"
    EXCHANGERATE_API_URL: str = "https://v6.exchangerate-api.com/v6"

    # Базовая валюта
    BASE_CURRENCY: str = "USD"

    # Списки валют с default_factory
    FIAT_CURRENCIES: Tuple[str, ...] = field(
        default_factory=lambda: ("EUR", "CAD", "JPY", "GBP", "AUD", "SCR", "RUB"))
    CRYPTO_CURRENCIES: Tuple[str, ...] = field(
        default_factory=lambda: ("BTC", "ETH", "SOL"))

    # Словарь с default_factory
    CRYPTO_ID_MAP: Dict[str, str] = field(default_factory=lambda: {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "SOL": "solana",
    })

    # Пути
    RATES_FILE_PATH: str = "data/rates.json"
    HISTORY_FILE_PATH: str = "data/exchange_rates.json"

    # Сетевые параметры
    REQUEST_TIMEOUT: int = 10
