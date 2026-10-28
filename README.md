# Academy Leads Backend

Backend для приема заявок с сайта Academy Crackenston и отправки их в Telegram-группу.

## Render

Build Command:

`pip install -r requirements.txt`

Start Command:

`gunicorn app:app`

Environment Variables:

- `BOT_TOKEN` — токен от BotFather
- `CHAT_ID` — ID вашей Telegram-группы, например `-1001234567890`
- `ALLOWED_ORIGINS` — на этапе теста можно `*`

После деплоя endpoint для сайта:

`https://ВАШ-СЕРВИС.onrender.com/api/lead`

Проверка backend:

`https://ВАШ-СЕРВИС.onrender.com/health`

Важно: не храните BOT_TOKEN в GitHub и не вставляйте его в HTML сайта.
