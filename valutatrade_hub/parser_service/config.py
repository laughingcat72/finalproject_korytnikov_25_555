
import os
from dataclasses import dataclass, field
from typing import Dict, Tuple


@dataclass
class ParserConfig:

    EXCHANGERATE_API_KEY: str = os.getenv("EXCHANGERATE_API_KEY", "")

    COINGECKO_URL: str = "https://api.coingecko.com/api/v3/simple/price"
    EXCHANGERATE_API_URL: str = "https://v6.exchangerate-api.com/v6"

    BASE_CURRENCY: str = "USD"

    FIAT_CURRENCIES: Tuple[str, ...] = field(
        default_factory=lambda: ("EUR", "CAD", "JPY", "GBP", "AUD", "SCR", "RUB"))
    CRYPTO_CURRENCIES: Tuple[str, ...] = field(
        default_factory=lambda: ("BTC", "ETH", "SOL"))

    CRYPTO_ID_MAP: Dict[str, str] = field(default_factory=lambda: {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "SOL": "solana",
    })

    RATES_FILE_PATH: str = "data/rates.json"
    HISTORY_FILE_PATH: str = "data/exchange_rates.json"

    REQUEST_TIMEOUT: int = 10
