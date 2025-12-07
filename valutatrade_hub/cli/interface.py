# cli/interface.py
import argparse
from ..core.usecases import AuthUseCase
from ..core.exceptions import InsufficientFundsError, CurrencyNotFoundError, ApiRequestError
from ..parser_service.updater import RatesUpdater
from ..parser_service.config import ParserConfig
from ..parser_service.storage import RatesStorage

auth_use_case = AuthUseCase()


def interface():
    parser = argparse.ArgumentParser(
        description="CLI Интерфейс ValutaTrade Hub")
    subparsers = parser.add_subparsers(
        dest="command", help="Доступные команды")

    # Команда register
    register_parser = subparsers.add_parser(
        "register", help="Регистрация нового пользователя")
    register_parser.add_argument("username", type=str, help="Имя пользователя")
    register_parser.add_argument("password", type=str, help="Пароль")

    # Команда login
    login_parser = subparsers.add_parser("login", help="Вход в систему")
    login_parser.add_argument("username", type=str, help="Имя пользователя")
    login_parser.add_argument("password", type=str, help="Пароль")

    # Команда buy
    buy_parser = subparsers.add_parser("buy", help="Купить валюту")
    buy_parser.add_argument("currency", type=str,
                            help="Код валюты (например, BTC)")
    buy_parser.add_argument("amount", type=float,
                            help="Количество для покупки")

    # Команда sell
    sell_parser = subparsers.add_parser("sell", help="Продать валюту")
    sell_parser.add_argument("currency", type=str, help="Код валюты")
    sell_parser.add_argument("amount", type=float,
                             help="Количество для продажи")

    # Команда get-rate (старая)
    get_rate_parser = subparsers.add_parser(
        "get-rate", help="Получить курс валюты")
    get_rate_parser.add_argument("currency", type=str, help="Исходная валюта")
    get_rate_parser.add_argument("tocurrency", type=str, help="Целевая валюта")

    # Команда show-portfolio
    show_portfolio_parser = subparsers.add_parser(
        "show-portfolio", help="Показать портфель")
    show_portfolio_parser.add_argument("--base", type=str, default="USD",
                                       help="Базовая валюта для конвертации (по умолчанию USD)")

    # ===== НОВЫЕ КОМАНДЫ ДЛЯ PARSER SERVICE =====

    # 1. Команда update-rates (строго по заданию)
    update_parser = subparsers.add_parser(
        "update-rates",
        help="Запустить немедленное обновление курсов валют"
    )
    update_parser.add_argument(
        "--source",
        type=str,
        choices=["coingecko", "exchangerate"],
        help="Обновить данные только из указанного источника"
    )

    # 2. Команда show-rates (улучшенная версия get-rate)
    show_rates_parser = subparsers.add_parser(
        "show-rates",
        help="Показать список актуальных курсов из локального кеша"
    )
    show_rates_parser.add_argument(
        "--currency",
        type=str,
        help="Показать курс только для указанной валюты"
    )
    show_rates_parser.add_argument(
        "--top",
        type=int,
        help="Показать N самых дорогих криптовалют"
    )
    show_rates_parser.add_argument(
        "--base",
        type=str,
        default="USD",
        help="Показать все курсы относительно указанной базы"
    )

    args = parser.parse_args()

    # Обработка команд
    try:
        if args.command == "register":
            auth_use_case.register(args.username, args.password)

        elif args.command == "login":
            auth_use_case.login(args.username, args.password)

        elif args.command == "buy":
            result = auth_use_case.buy(args.currency, args.amount)
            if not result:
                print("Покупка не выполнена. Проверьте введенные данные.")

        elif args.command == "sell":
            result = auth_use_case.sell(args.currency, args.amount)
            if not result:
                print("Продажа не выполнена. Проверьте введенные данные.")

        elif args.command == "show-portfolio":
            auth_use_case.show_portfolio(args.base)

        elif args.command == "get-rate":
            result = auth_use_case.get_rate(args.currency, args.tocurrency)
            if not result:
                print("Не удалось получить курс. Проверьте коды валют.")

        # ===== НОВЫЕ КОМАНДЫ =====

        elif args.command == "update-rates":
            _handle_update_rates(args.source)

        elif args.command == "show-rates":
            _handle_show_rates(args.currency, args.top, args.base)

        else:
            parser.print_help()

    # Обработка исключений
    except InsufficientFundsError as e:
        print(f"❌ {e}")
        print("   Проверьте баланс и повторите операцию.")

    except CurrencyNotFoundError as e:
        print(f"❌ {e}")
        print("   Используйте команду 'get-rate --from USD --to <валюта>' для проверки доступных валют")
        print("   Доступные валюты: USD, EUR, RUB, BTC, ETH")

    except ApiRequestError as e:
        print(f"❌ {e}")
        print("   Сервис курсов временно недоступен.")
        print("   Повторите попытку позже или проверьте подключение к сети.")

    except Exception as e:
        print(f"⚠️  Неизвестная ошибка: {e}")
        print("   Обратитесь к администратору системы.")


def _handle_update_rates(source: str = None):  # type: ignore
    """
    Обработчик команды update-rates (строго по заданию)
    """
    print("INFO: Starting rates update...")

    try:
        # Инициализируем ParserConfig
        config = ParserConfig()

        # Устанавливаем твой API ключ
        if not config.EXCHANGERATE_API_KEY:
            config.EXCHANGERATE_API_KEY = "71ccd029b9f44cf21cdf6fe7"

        updater = RatesUpdater(config)
        result = updater.run_update(source)

        if result["success"]:
            print(
                f"Update successful. Total rates updated: {result['total_rates']}")

            # Показываем обновленные пары
            if result["updated_pairs"]:
                print("Updated pairs:")
                for pair in result["updated_pairs"]:
                    print(f"  - {pair}")

            # Информация о кеше
            cache_info = updater.get_cache_info()
            print(f"Last refresh: {cache_info['last_refresh']}")

        else:
            print("Update completed with errors.")
            if result["errors"]:
                print("Errors:")
                for error in result["errors"]:
                    print(f"  - {error}")
            print("Check logs/actions.log for details.")

    except ApiRequestError as e:
        print(f"ERROR: Failed to update rates: {e}")
        print("Check your API key or network connection.")
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        print("Check logs/actions.log for details.")


def _handle_show_rates(currency: str = None, top: int = None, base: str = "USD"):  # type: ignore
    """
    Обработчик команды show-rates (строго по заданию)
    """
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

        # Фильтрация по валюте если указана
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

        # Сортировка
        sorted_items = sorted(filtered_pairs.items(), key=lambda x: x[0])

        # Если нужны топ N самых дорогих (только для крипты)
        if top:
            # Фильтруем только криптовалюты
            crypto_items = [(k, v) for k, v in sorted_items if any(
                crypto in k for crypto in ["BTC", "ETH", "SOL"])]
            # Сортируем по курсу (по убыванию)
            crypto_items.sort(key=lambda x: x[1]["rate"], reverse=True)
            sorted_items = crypto_items[:top]

        # Вывод результатов
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
