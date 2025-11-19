import argparse
from ..core.usecases import AuthUseCase

auth_use_case = AuthUseCase()


def interface():
    parser = argparse.ArgumentParser(description="CLI Интерфейс")
    subparsers = parser.add_subparsers(
        dest="command", help="Available commands")
    register_parser = subparsers.add_parser(
        "register", help="Register new user")
    register_parser.add_argument("username", type=str, help="Username")
    register_parser.add_argument("password", type=str, help="Password")

    register_login = subparsers.add_parser(
        "login", help="Register new user")
    register_login.add_argument("username", type=str, help="Username")
    register_login.add_argument("password", type=str, help="Password")

    register_buy = subparsers.add_parser(
        "buy", help="Register new user")
    register_buy.add_argument("currency", type=str, help="amount")
    register_buy.add_argument("amount", type=float, help="Username")

    register_get_rate = subparsers.add_parser(
        "get_rate", help="Register new user")
    register_get_rate.add_argument("currency", type=str, help="amount")
    register_get_rate.add_argument("tocurrency", type=str, help="Username")

    register_sell = subparsers.add_parser(
        "sell", help="Register new user")
    register_sell.add_argument("currency", type=str, help="amount")
    register_sell.add_argument("amount", type=float, help="Username")

    register_show = subparsers.add_parser(
        "show_portfolio", help="Register new user")

    args = parser.parse_args()
    if args.command == "register":
        auth_use_case.register(args.username, args.password)
    if args.command == "login":
        auth_use_case.login(args.username, args.password)
    if args.command == "buy":
        auth_use_case.buy(args.currency, args.amount)
    if args.command == "show_portfolio":
        auth_use_case.show_portfolio()
    if args.command == "get_rate":
        auth_use_case.get_rate(args.currency, args.tocurrency)
    if args.command == "sell":
        auth_use_case.sell(args.currency, args.amount)
