
class InsufficientFundsError(Exception):
    # Недостаточно средств на счете

    def __init__(self, currency_code: str, available: float, required: float):
        message = f"Недостаточно средств: доступно {available} {currency_code}, требуется {required} {currency_code}"
        super().__init__(message)


class CurrencyNotFoundError(Exception):
    # Валюта не найдена

    def __init__(self, currency_code: str):
        message = f"Неизвестная валюта '{currency_code}'"
        super().__init__(message)


class ApiRequestError(Exception):
    def __init__(self, reason: str = "неизвестная ошибка"):
        super().__init__(f"Ошибка при обращении к внешнему API: {reason}")
