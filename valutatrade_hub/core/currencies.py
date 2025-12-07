from .exceptions import CurrencyNotFoundError
from abc import ABC, abstractmethod


class Currency(ABC):
    def __init__(self, name: str, code: str):
        self._validate_code(code)
        self._validate_name(name)
        self._name = name

    def _validate_code(self, code: str):
        code_c = code.replace(' ', '').upper()

        if not code_c:
            raise ValueError("Код валюты не может быть пустым")
        if len(code_c) > 5:
            raise ValueError("Код валюты должен быть от 1 до 5 символов")
        if not code_c.isalpha():
            raise ValueError("Код валюты должен содержать только буквы")

        self._code = code_c

    def _validate_name(self, name: str):

        if not name or not name.strip():
            raise ValueError("Название не может быть пустым")

    @property
    def name(self):
        return self._name

    @property
    def code(self):
        return self._code

    @abstractmethod
    def get_display_info(self) -> str:
        pass


class FiatCurrency(Currency):
    def __init__(self, name: str, code: str, issuing_country: str):
        super().__init__(name, code)
        self._issuing_country = issuing_country

    @property
    def issuing_country(self):
        return self._issuing_country

    def get_display_info(self):
        return f"[FIAT] {self. code} — {self.name} (Issuing: {self.issuing_country})"


class CryptoCurrency(Currency):
    def __init__(self, name: str, code: str, algorithm: str, market_cap: float = 0.0):
        super().__init__(name, code)
        self._algorithm = algorithm
        self._market_cap = market_cap

    @property
    def algorithm(self):
        return self._algorithm

    @property
    def market_cap(self):
        return self._market_cap

    def get_display_info(self) -> str:
        return f"[CRYPTO] {self.code} — {self.name} (Algo: {self.algorithm}, MCAP: {self.market_cap:,.2f})"


KNOWN_CURRENCIES = {
    "USD": FiatCurrency("US Dollar", "USD", "United States"),
    "EUR": FiatCurrency("Euro", "EUR", "Eurozone"),
    "RUB": FiatCurrency("Russian Ruble", "RUB", "Russia",),
    "BTC": CryptoCurrency("Bitcoin", "BTC", "SHA-256", 1120000000000),
    "ETH": CryptoCurrency("Ethereum", "ETH", "Ethash", 372000000000)
}


def get_currency(code: str) -> Currency:
    code_clean = code.replace(' ', '').upper()
    if code_clean in KNOWN_CURRENCIES:
        return KNOWN_CURRENCIES[code_clean]
    raise CurrencyNotFoundError(code)
