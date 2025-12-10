import argparse
from ..core.usecases import AuthUseCase
from ..core.exceptions import InsufficientFundsError, CurrencyNotFoundError, ApiRequestError
from ..parser_service.updater import RatesUpdater
from ..parser_service.config import ParserConfig
from ..parser_service.storage import RatesStorage

auth_use_case = AuthUseCase()


def interface():
    # Проверяем наличие актуальных курсов при запуске
    try:
        from ..parser_service.updater import RatesUpdater
        from ..parser_service.config import ParserConfig

        config = ParserConfig()
        updater = RatesUpdater(config)
        cache_info = updater.get_cache_info()

        if cache_info['last_refresh'] == 'Никогда':
            print("⚠️  Курсы валют не загружены")
            print("   Используйте 'update-rates' для получения актуальных курсов")
            print("   До обновления будут использоваться базовые курсы\n")
    except (argparse.ArgumentError, SystemExit):
        pass
    parser = argparse.ArgumentParser(
        description="CLI Интерфейс ValutaTrade Hub",
        add_help=False,
        exit_on_error=False
    )

    subparsers = parser.add_subparsers(
        dest="command", help="Доступные команды", required=False)

    register_parser = subparsers.add_parser(
        "register", help="Регистрация нового пользователя")
    register_parser.add_argument("username", type=str, help="Имя пользователя")
    register_parser.add_argument("password", type=str, help="Пароль")

    login_parser = subparsers.add_parser("login", help="Вход в систему")
    login_parser.add_argument("username", type=str, help="Имя пользователя")
    login_parser.add_argument("password", type=str, help="Пароль")

    buy_parser = subparsers.add_parser("buy", help="Купить валюту")
    buy_parser.add_argument("currency", type=str, help="Код валюты")
    buy_parser.add_argument("amount", type=float,
                            help="Количество для покупки")

    sell_parser = subparsers.add_parser("sell", help="Продать валюту")
    sell_parser.add_argument("currency", type=str, help="Код валюты")
    sell_parser.add_argument("amount", type=float,
                             help="Количество для продажи")

    get_rate_parser = subparsers.add_parser(
        "get-rate", help="Получить курс валюты")
    get_rate_parser.add_argument("currency", type=str, help="Исходная валюта")
    get_rate_parser.add_argument("tocurrency", type=str, help="Целевая валюта")

    show_portfolio_parser = subparsers.add_parser(
        "show-portfolio", help="Показать портфель")
    show_portfolio_parser.add_argument(
        "--base", type=str, default="USD", help="Базовая валюта")

    update_parser = subparsers.add_parser(
        "update-rates", help="Обновить курсы валют")
    update_parser.add_argument(
        "--source", type=str, choices=["coingecko", "exchangerate"], help="Источник")

    show_rates_parser = subparsers.add_parser(
        "show-rates", help="Показать курсы из кеша")
    show_rates_parser.add_argument(
        "--currency", type=str, help="Фильтр по валюте")
    show_rates_parser.add_argument("--top", type=int, help="Топ N криптовалют")
    show_rates_parser.add_argument(
        "--base", type=str, default="USD", help="Базовая валюта")

    try:
        args = parser.parse_args()
    except argparse.ArgumentError as e:
        print(f"❌ Ошибка в аргументах: {e}")
        return
    except SystemExit:
        return

    if not args.command:
        return

    try:
        if args.command == "register":
            auth_use_case.register(args.username, args.password)

        elif args.command == "login":
            auth_use_case.login(args.username, args.password)

        elif args.command == "buy":
            result = auth_use_case.buy(args.currency, args.amount)
            if not result:
                print("Покупка не выполнена.")

        elif args.command == "sell":
            result = auth_use_case.sell(args.currency, args.amount)
            if not result:
                print("Продажа не выполнена.")

        elif args.command == "show-portfolio":
            auth_use_case.show_portfolio(args.base)

        elif args.command == "get-rate":
            result = auth_use_case.get_rate(args.currency, args.tocurrency)
            if not result:
                print("Не удалось получить курс.")

        elif args.command == "update-rates":
            _handle_update_rates(args.source)

        elif args.command == "show-rates":
            _handle_show_rates(args.currency, args.top, args.base)

    except InsufficientFundsError as e:
        print(f"❌ {e}")
        print("   Проверьте баланс.")
    except CurrencyNotFoundError as e:
        print(f"❌ {e}")
        print("   Доступные валюты: USD, EUR, RUB, BTC, ETH")
    except ApiRequestError as e:
        print(f"❌ {e}")
        print("   Сервис курсов недоступен.")
    except Exception as e:
        print(f"⚠️  Ошибка: {e}")
        print("   Обратитесь к администратору.")


def _handle_update_rates(source=None):
    print("INFO: Starting rates update...")
    try:
        config = ParserConfig()
        if not config.EXCHANGERATE_API_KEY:
            config.EXCHANGERATE_API_KEY = "71ccd029b9f44cf21cdf6fe7"
        updater = RatesUpdater(config)
        result = updater.run_update(source)  # type: ignore
        if result["success"]:
            print(
                f"Update successful. Total rates updated: {result['total_rates']}")
            if result["updated_pairs"]:
                print("Updated pairs:")
                for pair in result["updated_pairs"]:
                    print(f"  - {pair}")
            cache_info = updater.get_cache_info()
            print(f"Last refresh: {cache_info['last_refresh']}")
        else:
            print("Update completed with errors.")
            if result["errors"]:
                print("Errors:")
                for error in result["errors"]:
                    print(f"  - {error}")
    except ApiRequestError as e:
        print(f"ERROR: Failed to update rates: {e}")
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")


def _handle_show_rates(currency=None, top=None, base="USD"):
    try:
        config = ParserConfig()
        storage = RatesStorage(config.RATES_FILE_PATH,
                               config.HISTORY_FILE_PATH)
        data = storage.get_current_rates()
        pairs = data.get("pairs", {})
        last_refresh = data.get("last_refresh", "Never")
        if not pairs:
            print("Локальный кеш курсов пуст.")
            print("Выполните 'update-rates', чтобы загрузить данные.")
            return
        print(f"Rates from cache (updated at {last_refresh}):")
        print("-" * 40)
        filtered_pairs = {}
        if currency:
            currency = currency.upper()
            for pair_key, rate_data in pairs.items():
                if currency in pair_key:
                    filtered_pairs[pair_key] = rate_data
            if not filtered_pairs:
                print(f"Курс для '{currency}' не найден в кеше.")
                return
        else:
            filtered_pairs = pairs
        sorted_items = sorted(filtered_pairs.items(), key=lambda x: x[0])
        if top:
            crypto_items = [(k, v) for k, v in sorted_items if any(
                crypto in k for crypto in ["BTC", "ETH", "SOL"])]
            crypto_items.sort(key=lambda x: x[1]["rate"], reverse=True)
            sorted_items = crypto_items[:top]
        for pair_key, rate_data in sorted_items:
            rate = rate_data["rate"]
            source = rate_data["source"]
            updated = rate_data["updated_at"]
            print(
                f"- {pair_key}: {rate:,.4f}  (source: {source}, updated: {updated})")
        print("-" * 40)
        print(f"Total pairs: {len(sorted_items)}")
    except Exception as e:
        print(f"Ошибка при получении курсов: {e}")
        print("Выполните 'update-rates' для обновления данных.")


if __name__ == "__main__":
    interface()
