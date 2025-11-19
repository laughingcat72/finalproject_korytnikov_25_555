from valutatrade_hub.cli.interface import interface

if __name__ == "__main__":
    print("для выхода введите 'exit'")

    while True:
        try:
            command = input("\nВведите команду: ").strip()
            if command.lower() == 'exit':
                break

            import sys
            sys.argv = ['main.py'] + command.split()
            interface()

        except Exception as e:
            print(f"Ошибка: {e}")
