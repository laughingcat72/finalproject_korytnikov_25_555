
import sys
import shlex


def get_time_based_greeting():
    """Возвращает приветствие в зависимости от времени суток"""
    from datetime import datetime

    current_hour = datetime.now().hour

    if 5 <= current_hour < 12:
        return "🌅 Доброе утро!"
    elif 12 <= current_hour < 18:
        return "☀️  Добрый день!"
    elif 18 <= current_hour < 23:
        return "🌇 Добрый вечер!"
    else:
        return "🌙 Доброй ночи!"


def show_welcome():
    """Показывает приветственное сообщение"""
    from datetime import datetime

    greeting = get_time_based_greeting()
    current_time = datetime.now().strftime("%H:%M")

    print(f"""
{greeting}
⏰ Сейчас {current_time}

═══════════════════════════════════════════
    KORYTNIKOV HUB - Торговый кошелек
═══════════════════════════════════════════
💡 Введите команду или 'help' для справки
🚪 Для выхода введите 'exit'
═══════════════════════════════════════════
""")


def show_help():
    """Показывает справку по командам"""
    print("""
📋 ДОСТУПНЫЕ КОМАНДЫ:
  register <user> <pass>     📝 Регистрация
  login <user> <pass>        🔑 Вход в систему
  buy <валюта> <количество>  💰 Купить валюту
  sell <валюта> <количество> 💸 Продать валюту
  show-portfolio             📊 Показать портфель
  show-rates                 📈 Показать курсы
  update-rates               🔄 Обновить курсы
  get-rate <из> <в>          💱 Получить курс

🎯 Примеры:
  register alice 1234
  login alice 1234
  buy BTC 0.1
  show-rates --currency EUR

⚙️  Служебные:
  help      ❓ Эта справка
  exit      🚪 Выход из программы
""")


def main():
    """Главная функция с интерактивным циклом"""

    show_welcome()

    while True:
        try:

            user_input = input("\n💲 Введите команду: ").strip()

            if user_input.lower() in ['exit', 'quit', 'выход']:
                print("\n👋 До свидания! Ждем вас снова!")
                break

            if user_input.lower() in ['help', 'помощь', '?']:
                show_help()
                continue

            if not user_input:
                print("❌ Пустая команда. Введите 'help' для справки")
                continue

            try:
                args = shlex.split(user_input)
            except ValueError as e:
                print(f"❌ Ошибка в команде: {e}")
                print("   Используйте кавычки для строк с пробелами")
                print("   Пример: register \"Иван Иванов\" password123")
                continue

            original_argv = sys.argv.copy()
            sys.argv = ['main.py'] + args

            try:

                from valutatrade_hub.cli.interface import interface
                interface()
            finally:
                sys.argv = original_argv

        except KeyboardInterrupt:
            print("\n\n👋 До свидания!")
            break
        except SystemExit:

            continue
        except Exception as e:
            print(f"⚠️  Ошибка: {e}")
            print("   Попробуйте снова или введите 'help'")


if __name__ == "__main__":
    main()
