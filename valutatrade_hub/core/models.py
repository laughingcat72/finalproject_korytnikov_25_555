import secrets
import hashlib
from datetime import datetime


class User:
    def __init__(self, user_id: int, username: str, password: str):
        self._user_id = user_id
        self._username = username
        self._salt = self._generate_salt()
        self._hashed_password = self._hash_password(password)
        self._registration_date = datetime.now()

    def _generate_salt(self):
        return secrets.token_hex(8)

    def _hash_password(self, password: str):
        password_with_salt = password + self._salt
        password_bytes = password_with_salt.encode('utf-8')
        hash_object = hashlib.sha256(password_bytes)
        return hash_object.hexdigest()

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def username(self) -> str:
        return self._username

    @username.setter
    def username(self, ss: str):
        if not ss or not ss.strip():
            raise ValueError('Не может быть пустым')
        self._username = ss.strip()

    @property
    def registration_date(self) -> datetime:
        return self._registration_date

    def get_user_info(self) -> dict:
        return {
            "user_id": self._user_id,
            "username": self._username,
            "registration_date": self._registration_date.isoformat()
        }

    def verify_password(self, password: str) -> bool:
        return self._hash_password(password) == self._hashed_password

    def change_password(self, new_password: str):
        if len(new_password) < 4:
            raise ValueError('Пароль должен быть больше 4 символов!')
        self._salt = self._generate_salt()
        self._hashed_password = self._hash_password(new_password)

    @property
    def salt(self):
        return self._salt

    @property
    def hashed_password(self):
        return self._hashed_password

    def get_user(self):
        return {
            "user_id": self.user_id,
            "username":  self.username,
            "salt": self.salt,
            "hashed_password": self.hashed_password,
            "registration_date": self.registration_date.isoformat()
        }


class Wallet:
    def __init__(self, code: str, balance: float = 0.0):
        self._balance = balance
        self.currency_code = code

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value: float):
        if not isinstance(value, (float, int)):
            raise TypeError('Баланс должен быть числом!')

        if value < 0:
            raise ValueError('Баланс не может быть отрицальным!')
        self._balance = float(value)

    def deposit(self, a: float):
        if not isinstance(a, (float, int)):
            raise TypeError('Депозит должен быть числом!')
        if a <= 0:
            raise ValueError('Депозит не может быть отрицальным!')
        self._balance += a

    def withdraw(self, a: float):
        if not isinstance(a, (float, int)):
            raise TypeError('Сумма снятия должена быть числом!')
        if a <= 0:
            raise ValueError('Сумма снятия должна быть положительная!')
        self._balance -= a
        if a > self._balance:
            raise ValueError('Недостаточно средств!')

    def get_balance_info(self):
        return f'{self.currency_code}:{self._balance}'

    def __repr__(self):
        return f"Wallet('{self.currency_code}', {self.balance})"


class Portfolio:
    KURSS_VALUT = {
        'USD': 1.0,
        'EUR': 0.93,
        'BTC': 45000.0,
        'RUB': 0.011
    }

    def __init__(self, user_id: int, wallets):
        self._user_id = user_id
        self._wallets = wallets or {}

    @property
    def user_id(self):
        return self._user_id

    @property
    def wallets(self):
        return self._wallets.copy()

    def add_currency(self, currency_code: str):
        if currency_code in self._wallets:
            raise ValueError('Валюта уже есть!')
        new_wallet = Wallet(currency_code, 0.0)
        self._wallets[currency_code] = new_wallet

    def get_wallet(self, currency_code: str):
        if currency_code in self._wallets:
            return self._wallets[currency_code]
        else:
            raise ValueError(f'Ошибка,{currency_code} не найдена!')

    def get_total_value(self):
        total = 0.0
        for currency_code, wallet in self._wallets.items():
            balance = wallet.balance
            a = self.KURSS_VALUT[currency_code]*balance
            total += a
        return total

    def get_porfolio_data(self):

        return {'user_id': self.user_id,
                'wallets': self.wallets}
