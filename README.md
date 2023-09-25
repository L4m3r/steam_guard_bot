# steam_guard_bot

## Описание
Steam Guard Bot - это Telegram-бот, разработанный на Python, который обеспечивает генерацию и предоставление кодов аутентификации Steam Guard пользователям. Бот работает с помощью WebHooks и может быть легко развернут с использованием Docker Compose.

## Технологии
- Python
- [telebot](https://github.com/eternnoir/pyTelegramBotAPI)
- MySQL
- Docker Compose

## Установка
Для установки проекта выполните следующие шаги:

1. Клонируйте репозиторий на свой локальный компьютер:
```
git clone https://github.com/L4m3r/steam_guard_bot.git
cd steam_guard_bot
```
2. Создайте файл `.env` в корне проекта и добавьте в него следующие значения:
```
BOT_TOKEN=""
MYSQL_HOST="db"
MYSQL_DATABASE=""
MYSQL_USER=""
MYSQL_PASSWORD=""
MYSQL_ROOT_PASSWORD=""
WEBHOOK_HOST=""
WEBHOOK_PORT=""
WEBHOOK_LISTEN="bot"
```
3. Запустите приложение с помощью Docker Compose:
```
docker-compose up -d --build
```

## Лицензия
Проект распространяется под лицензией MIT. Подробности можно найти в файле [LICENSE](./LICENSE).
