# valutatrade_hub/core/usecases.py
from .models import User, Portfolio
from .utils import FileManager
from .exceptions import InsufficientFundsError
from .currencies import get_currency
from .exceptions import CurrencyNotFoundError
from ..decorators import log_action
from ..infra.settings import SettingsLoader
from ..infra.database import DatabaseManager
from ..parser_service.updater import RatesUpdater
from ..parser_service.config import ParserConfig


class AuthUseCase:
    def __init__(self):
        self.file_manager = FileManager()
        self.current_user = None
        self.settings = SettingsLoader()
        self.database = DatabaseManager()

        self.rates_config = ParserConfig()
        self.rates_updater = RatesUpdater(self.rates_config)

        self.static_rates = {
            'USD': 1.0,
            'EUR': 0.93,
            'BTC': 45000.0,
            'RUB': 0.011,
            'ETH': 2500.0,
            'SOL': 100.0,
            'SCR': 0.075
        }

        print("✅ Загрузчик курсов инициализирован")

    def _gen_user_id(self) -> int:
        users = self.file_manager.read_json(filename='users.json', default=[])
        if not users:
            return 1
        return max(user.get('user_id', 0) for user in users) + 1

    def _user_exists(self, username: str):
        users = self.file_manager.read_json('users.json',  [])
        for user in users:  # type: ignore
            if user['username'] == username:
                return True
        return False

    @log_action(action_name="REGISTER")
    def register(self, username: str, password: str):
        try:
            print('user')
            if not self._user_exists(username):
                user_id = self._gen_user_id()
                user = User(user_id, username, password)
                port = Portfolio(user_id, {})
                user_data = user.get_user()
                portfolio_data = port.get_porfolio_data()
                self.file_manager.write_json(
                    filename='users.json', data=user_data)
                self.file_manager.write_json(
                    filename='portfolios.json', data=portfolio_data)
                print(f"✅ Пользователь {username} успешно зарегистрирован!")
                return True

            else:
                print("❌ Пользователь c таким именем уже сущесвует!")
                return False
        except FileNotFoundError:
            print("❌ Файл с пользователями не найден")
            return False
        except PermissionError:
            print("❌ Нет доступа к файлам пользователей!")
            return False
        except Exception as e:
            print(f"❌ Неизвестная ошибка: {e}")
            return False

    @log_action(action_name="LOGIN")
    def login(self, username: str, password: str):
        users = self.file_manager.read_json('users.json', [])
        for user_data in users:  # type: ignore
            if user_data['username'] == username:

                user = User(user_data['user_id'], username, '')
                user._salt = user_data['salt']
                user._hashed_password = user_data['hashed_password']
                if user.verify_password(password):
                    self.current_user = user
                    print(f'✅ Добро пожаловать {username}!')
                    return True

                else:
                    print('❌ Неверный логин или пароль!')
                    return False

    def _get_dynamic_rate(self, from_currency: str, to_currency: str = "USD"):

        try:
            from_currency = from_currency.upper()
            to_currency = to_currency.upper()

            storage = self.rates_updater.storage
            data = storage.get_current_rates()

            if not data or "pairs" not in data:

                return None

            pairs = data.get("pairs", {})

            pair_key = f"{from_currency}_{to_currency}"

            if pair_key in pairs:
                rate = pairs[pair_key].get("rate")

                return rate

            reverse_key = f"{to_currency}_{from_currency}"

            if reverse_key in pairs:
                rate = pairs[reverse_key].get("rate")

                if rate and rate != 0:
                    return 1 / rate

            return None

        except Exception as e:
            print(f"DEBUG: Ошибка в _get_dynamic_rate: {e}")
            return None

    def _get_current_rate(self, from_currency: str, to_currency: str = "USD"):
        """Получает текущий курс (динамический или статический)"""

        dynamic_rate = self._get_dynamic_rate(from_currency, to_currency)
        if dynamic_rate:
            return dynamic_rate

        return self._get_static_rate(from_currency, to_currency)

    def _get_static_rate(self, from_currency: str, to_currency: str):
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        if from_currency == to_currency:
            return 1.0

        from_rate = self.static_rates.get(from_currency)
        to_rate = self.static_rates.get(to_currency)

        if from_rate is not None and to_rate is not None:
            if to_rate != 0:
                return from_rate / to_rate
            return 1.0

        if from_currency == "USD" and to_rate is not None:
            if to_rate != 0:
                return 1 / to_rate

        if to_currency == "USD" and from_rate is not None:
            return from_rate

        print(f"⚠️  Нет статического курса для {from_currency}→{to_currency}")
        return 1.0

    def show_portfolio(self, base_currency: str = "USD"):
        if self.current_user is None:
            print("❌ Сначала выполните login")
            return

        user_id = self.current_user._user_id
        port = self.file_manager.read_json('portfolios.json', [])
        user_portfolio = None

        for portfolios_data in port:
            if portfolios_data['user_id'] == user_id:
                user_portfolio = portfolios_data
                break

        if user_portfolio is None:
            print("ℹ️  У вас пока нет портфеля")
            return

        wallets_data = user_portfolio.get('wallets', {})
        if not wallets_data:
            print('ℹ️  У вас пока нет кошельков')
            return

        crypto_currencies = ['BTC', 'ETH', 'SOL']
        fiat_currencies = ['USD', 'EUR', 'RUB',
                           'SCR', 'JPY', 'GBP', 'CAD', 'AUD']

        print(
            f"📊 Портфель пользователя '{self.current_user.username}' (база: {base_currency}):")
        print("=" * 70)

        total_value = 0
        print(f"{'Валюта':<8} {'Баланс':<20} {'Курс':<15} {'Стоимость':<20}")
        print("-" * 70)

        for currency, balance in wallets_data.items():
            if currency in fiat_currencies:
                balance = float(balance)
                rate = self._get_current_rate(currency, base_currency)
                value = balance * rate
                total_value += value

                print(
                    f"{currency:<8} {balance:<20.2f} {rate:<15.4f} {value:<20.2f} {base_currency}")

        for currency, balance in wallets_data.items():
            if currency in crypto_currencies:
                balance = float(balance)
                rate = self._get_current_rate(currency, base_currency)
                value = balance * rate
                total_value += value

                # Для криптовалют - 8 знаков после запятой
                print(
                    f"{currency:<8} {balance:<20.8f} {rate:<15.2f} {value:<20.2f} {base_currency}")

        for currency, balance in wallets_data.items():
            if currency not in fiat_currencies and currency not in crypto_currencies:
                balance = float(balance)
                rate = self._get_current_rate(currency, base_currency)
                value = balance * rate
                total_value += value

                print(
                    f"{currency:<8} {balance:<20.2f} {rate:<15.4f} {value:<20.2f} {base_currency}")

        print("=" * 70)
        print(f"💰 ИТОГО: {total_value:,.2f} {base_currency}")

        cache_info = self.rates_updater.get_cache_info()
        print(f"\n🕐 Курсы обновлены: {cache_info['last_refresh']}")

    @log_action(action_name="BUY", verbose=True)
    def buy(self, currency: str, amount: float):
        if self.current_user is None:
            print("❌ Сначала выполните login")
            return False

        try:
            if amount <= 0:
                print("❌ 'amount' должен быть положительным числом")
                return False

            get_currency(currency)
            currency = currency.upper()
            user_id = self.current_user._user_id

            current_rate = self._get_current_rate(currency, "USD")

            portfolios = self.file_manager.read_json('portfolios.json', [])
            user_portfolio_data = None

            for portfolio_data in portfolios:
                if portfolio_data['user_id'] == user_id:
                    user_portfolio_data = portfolio_data
                    break

            if user_portfolio_data is None:
                user_portfolio_data = {'user_id': user_id, 'wallets': {}}
                portfolios.append(user_portfolio_data)

            wallets_data = user_portfolio_data.get('wallets', {})
            if currency not in wallets_data:
                wallets_data[currency] = 0.0

            old_balance = wallets_data[currency]
            wallets_data[currency] += amount
            user_portfolio_data['wallets'] = wallets_data

            cost = amount * current_rate

            self.file_manager.update_json('portfolios.json', portfolios)

            print("\n✅ Покупка выполнена успешно!")
            print(f"   📈 Куплено: {amount} {currency}")
            print(f"   💱 Курс: {current_rate:,.4f} USD/{currency}")
            print(f"   💰 Стоимость: {cost:,.2f} USD")

            if currency in ['BTC', 'ETH', 'SOL']:
                print(
                    f"   📊 Баланс {currency}: {old_balance:.8f} → {wallets_data[currency]:.8f}")
            else:

                print(
                    f"   📊 Баланс {currency}: {old_balance:.2f} → {wallets_data[currency]:.2f}")

            return True

        except CurrencyNotFoundError as e:
            print(f"❌ Ошибка: {e}")
            return False
        except Exception as e:
            print(f"❌ Ошибка при покупке: {e}")
            return False

    @log_action(action_name="SELL", verbose=True)
    def sell(self, currency: str, amount: float):
        if self.current_user is None:
            print("❌ Сначала выполните login")
            return False

        try:
            if amount <= 0:
                print('❌ Сумма должна быть положительной!')
                return False

            get_currency(currency)
            currency = currency.upper()
            user_id = self.current_user._user_id

            current_rate = self._get_current_rate(currency, "USD")

            port = self.file_manager.read_json('portfolios.json', [])
            user_port = None

            for portfolio_data in port:
                if portfolio_data['user_id'] == user_id:
                    user_port = portfolio_data
                    break

            if user_port is None:
                user_port = {'user_id': user_id, 'wallets': {}}
                port.append(user_port)

            wallets = user_port.get('wallets', {})
            if currency not in wallets:
                print(f'❌ У вас нет кошелька {currency}.')
                return False

            old_balance = wallets[currency]

            if old_balance < amount:
                raise InsufficientFundsError(currency, old_balance, amount)

            new_balance = old_balance - amount
            wallets[currency] = new_balance

            cost = amount * current_rate

            self.file_manager.update_json('portfolios.json', port)

            print("\n✅ Продажа выполнена успешно!")
            print(f"   📉 Продано: {amount} {currency}")
            print(f"   💱 Курс: {current_rate:,.4f} USD/{currency}")
            print(f"   💰 Сумма: {cost:,.2f} USD")
            if currency in ['BTC', 'ETH', 'SOL']:
                print(
                    f"   📊 Баланс {currency}: {old_balance:.8f} → {new_balance:.8f}")
            else:
                print(
                    f"   📊 Баланс {currency}: {old_balance:.2f} → {new_balance:.2f}")
            return True

        except CurrencyNotFoundError as e:
            print(f"❌ Ошибка: {e}")
            return False
        except InsufficientFundsError as e:
            print(f"❌ {e}")
            return False
        except Exception as e:
            print(f"❌ Ошибка при продаже: {e}")
            return False

    @log_action(action_name="GET_RATE")
    def get_rate(self, currency: str, tocurrency: str):
        try:
            get_currency(currency)
            get_currency(tocurrency)

            rate = self._get_current_rate(currency, tocurrency)

            print(f"\n📊 Курс {currency} → {tocurrency}:")
            print(f"   💱 1 {currency} = {rate:,.8f} {tocurrency}")
            print(f"   🔄 1 {tocurrency} = {1/rate:,.8f} {currency}")

            cache_info = self.rates_updater.get_cache_info()
            if cache_info['last_refresh'] != 'Никогда':
                print("\n💡 Курс взят из кеша")
                print(f"   🕐 Обновлён: {cache_info['last_refresh']}")
                if cache_info['pairs_count'] > 0:
                    print(
                        f"   📈 В кеше: {cache_info['pairs_count']} пар валют")
            else:
                print("\n⚠️  Используется базовый курс (кеш пуст)")
                print("   💡 Выполните 'update-rates' для получения актуальных курсов")

            return True

        except CurrencyNotFoundError as e:
            print(f"❌ Ошибка: {e}")
            return False
        except Exception as e:
            print(f"❌ Ошибка при получении курса: {e}")
            return False

    def _is_cache_expired(self, ttl: int) -> bool:
        """Проверяет устарел ли кеш курсов"""
        return False
