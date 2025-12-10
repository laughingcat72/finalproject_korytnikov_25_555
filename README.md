# ValutaTrade Hub

CLI для торговли валютами и криптой. Регистрация, вход, покупка/продажа, портфель, актуальные курсы.

## 🚀 Быстрый старт

```bash
# Установи зависимости
poetry install

# Запусти
poetry run project
📦 Установка
Через Poetry (лучше)
bash
poetry install
poetry run project
Через pip
bash
pip install -r requirements.txt
python main.py
💻 Команды
Базовые
bash
project register юзер пароль
project login юзер пароль
Торговля
bash
project buy BTC 0.5     # Купить биткоин
project sell EUR 100    # Продать евро
project show-portfolio  # Портфель
Курсы
bash
project update-rates           # Обновить курсы
project get-rate BTC USD       # Курс биткоина
project show-rates --top 5     # Топ-5 крипты
⚙️ API Ключ
Для фиатных курсов нужен ключ exchangerate-api.com:

Получи ключ на сайте

Создай файл .env:

text
EXCHANGERATE_API_KEY=твой_ключ
📁 Структура
text
data/              # База (JSON)
├── users.json
├── portfolios.json
├── rates.json     # Кэш курсов (TTL: 300с)
└── exchange_rates.json

logs/actions.log   # Логи
🛠️ Для разработки
bash
make lint     # Проверка кода
make format   # Форматирование
make build    # Сборка пакета
🐛 Если не работает
poetry install не сделал? → удали poetry.lock и повтори

Курсы старые? → project update-rates

