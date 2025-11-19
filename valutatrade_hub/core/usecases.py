from .models import User, Portfolio
from .utils import FileManager
from datetime import datetime


class AuthUseCase:
    def __init__(self):
        self.file_manager = FileManager()
        self.current_user = None

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
                print(f"Пользователь {username} успешно зарегистрирован!")
                return True

            else:
                print("Пользователь c таким именем уже сущесвует!")
                return False
        except FileNotFoundError:
            print("Файл с пользователями не найден")
            return False
        except PermissionError:
            print("Нет доступа к файлам пользователей!")
            return False
        except Exception as e:
            print(f"Неизвестная ошибка: {e}")
            return False

    def login(self, username: str, password: str):
        users = self.file_manager.read_json('users.json', [])
        for user_data in users:  # type: ignore
            if user_data['username'] == username:

                user = User(user_data['user_id'], username, '')
                user._salt = user_data['salt']
                user._hashed_password = user_data['hashed_password']
                if user.verify_password(password):
                    self.current_user = user
                    print(f'Добро пожаловать {username}!')
                    return True

                else:
                    print('Неверный логин или пароль!')
                    return False

    def show_portfolio(self, base_currency: str = "USD"):

        if self.current_user is None:
            print("Сначала выполните login")
            return
        user_id = self.current_user._user_id
        port = self.file_manager.read_json('portfolios.json', [])
        user_portfolio = None
        for portfolios_data in port:
            if portfolios_data['user_id'] == user_id:
                user_portfolio = portfolios_data
                break
        else:
            print("У вас пока нет портфеля")
            return
        if base_currency not in Portfolio.KURSS_VALUT:
            print(f"Неизвестная базовая валюта '{base_currency}'")
            return
        wallets_data = user_portfolio.get('wallets', {})
        if not wallets_data:
            print('У вас пока нет кошельков')
            return
        print(
            f"Портфель пользователя '{self.current_user.username}' (база: USD):")

        total_in_usd = 0
        for currency, balance in wallets_data.items():
            balance = float(balance)
            value_in_usd = balance * Portfolio.KURSS_VALUT.get(currency, 1.0)
            total_in_usd += value_in_usd

            if currency == "USD":
                print(
                    f"  - {currency}: {balance:,.2f}  → {value_in_usd:,.2f} USD")
            else:
                print(
                    f"  - {currency}: {balance:.4f}  → {value_in_usd:,.2f} USD")

        print("  ---------------------------------")
        print(f"  ИТОГО: {total_in_usd:,.2f} USD")

    def buy(self, currency: str, amount: float):
        if self.current_user is None:
            print("Сначала выполните login")
            return False
        if not currency or len(currency) != 3 or not currency.isalpha():
            print("Некорректный код валюты")
            return False

        if amount <= 0:
            print("'amount' должен быть положительным числом")
            return False
        currency = currency.upper()
        user_id = self.current_user._user_id
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
        cost = amount*Portfolio.KURSS_VALUT[currency]
        self.file_manager.update_json('portfolios.json', portfolios)
        print(
            f"Покупка выполнена: {amount} {currency} по курсу {Portfolio.KURSS_VALUT[currency]:} USD/{currency}")
        print('Изменения в портфеле:')
        print(
            f"- {currency}: было {old_balance} → стало {wallets_data[currency]}")
        print(f"Оценочная стоимость покупки: {cost} USD")

    def sell(self, currency: str, amount: float):
        if self.current_user is None:
            print("Сначала выполните login")
            return False
        if not currency or len(currency) != 3 or not currency.isalpha():
            print('Неверный код валюты')
            return False
        if amount <= 0:
            print('Положительное число!')
            return False

        currency = currency.upper()
        user_id = self.current_user._user_id
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
            print(
                f'У вас нет кошелька {currency}. Добавьте валюту: она создаётся автоматически при первой покупке.')
            return False

        old_balance = wallets[currency]
        if old_balance < amount:
            print(
                f'Недостаточно средств: доступно {old_balance} {currency}, требуется {amount} {currency}')
            return False
        else:
            new_balance = old_balance - amount
        wallets[currency] = new_balance
        cost = amount*Portfolio.KURSS_VALUT[currency]
        self.file_manager.update_json('portfolios.json', port)
        print(
            f"Продажа выполнена: {amount} {currency} по курсу {Portfolio.KURSS_VALUT[currency]:} USD/{currency}")
        print('Изменения в портфеле:')
        print(f"- {currency}: было {old_balance} → стало {new_balance}")
        print(f"Оценочная стоимость продажи: {cost} USD")
        return True

    def get_rate(self, currency: str, tocurrency: str):
        if not currency and tocurrency or len(currency) != 3 or not currency.isalpha() and tocurrency.isalpha():
            print("Некорректный код валюты")
            return False

        if currency and tocurrency not in Portfolio.KURSS_VALUT:
            print("Некорректный код валюты")
            return False

        a = Portfolio.KURSS_VALUT[currency]
        b = Portfolio.KURSS_VALUT[tocurrency]
        rate = a / b
        print(f"Курс {currency}→{tocurrency}: {rate:.8f}")
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"(обновлено: {current_time})")
        reverse_rate = 1 / rate
        print(f"Обратный курс {tocurrency}→{currency}: {reverse_rate:.2f}")
