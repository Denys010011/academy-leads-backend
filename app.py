import os
import html

from flask import Flask, jsonify, request
from flask_cors import CORS
import telebot

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
CHAT_ID = os.getenv("CHAT_ID", "").strip()
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").strip()

if ALLOWED_ORIGINS == "*":
    cors_origins = "*"
else:
    cors_origins = [x.strip() for x in ALLOWED_ORIGINS.split(",") if x.strip()]

CORS(
    app,
    resources={r"/api/*": {"origins": cors_origins}},
    methods=["POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML") if BOT_TOKEN else None


def clean(value, max_len=2000):
    if value is None:
        return ""
    value = str(value).strip()
    if len(value) > max_len:
        value = value[:max_len]
    return html.escape(value)


def build_message(data):
    form_type = clean(
        data.get("type")
        or data.get("form_type")
        or data.get("source")
        or "Заявка"
    )

    name = clean(data.get("name") or data.get("full_name") or data.get("fname"))
    phone = clean(
        data.get("phone")
        or data.get("contact")
        or data.get("fcontact")
        or data.get("tcontact")
    )
    comment = clean(
        data.get("comment")
        or data.get("message")
        or data.get("info")
        or data.get("finfo")
        or data.get("about")
        or data.get("tabout"),
        3000,
    )
    subject = clean(data.get("subject") or data.get("fsubj") or data.get("tsubj"))
    experience = clean(data.get("experience") or data.get("texp"))

    type_lower = form_type.lower()

    if "мотива" in type_lower or "motivation" in type_lower:
        title = "📝 <b>НОВА ЗАЯВКА — МОТИВАЦІЙНИЙ ЛИСТ</b>"
    elif "виклад" in type_lower or "teacher" in type_lower:
        title = "👨‍🏫 <b>НОВА ЗАЯВКА ВІД ВИКЛАДАЧА</b>"
    else:
        title = "🎓 <b>НОВА ЗАЯВКА — ПРОБНЕ ЗАНЯТТЯ</b>"

    lines = [title, ""]

    if name:
        lines.append(f"👤 <b>Ім'я:</b> {name}")
    if phone:
        lines.append(f"📞 <b>Телефон / контакт:</b> {phone}")
    if subject:
        lines.append(f"📚 <b>Предмет:</b> {subject}")
    if experience:
        lines.append(f"🕒 <b>Досвід:</b> {experience}")
    if comment:
        lines.extend(["", f"💬 <b>Коментар:</b>\n{comment}"])

    return "\n".join(lines)


@app.get("/")
def index():
    return jsonify(ok=True, service="academy-leads-backend", message="Backend is running")


@app.get("/health")
def health():
    return jsonify(ok=True, bot_configured=bool(BOT_TOKEN), chat_configured=bool(CHAT_ID))


@app.post("/api/lead")
def api_lead():
    if not BOT_TOKEN or not CHAT_ID or bot is None:
        return jsonify(ok=False, error="Server is not configured. BOT_TOKEN or CHAT_ID is missing."), 500

    data = request.get_json(silent=True) or {}

    if str(data.get("website", "")).strip():
        return jsonify(ok=True), 200

    name = str(data.get("name") or data.get("full_name") or data.get("fname") or "").strip()
    phone = str(
        data.get("phone")
        or data.get("contact")
        or data.get("fcontact")
        or data.get("tcontact")
        or ""
    ).strip()

    if not name:
        return jsonify(ok=False, error="Ім'я обов'язкове"), 400

    if not phone:
        return jsonify(ok=False, error="Номер телефону / контакт обов'язковий"), 400

    try:
        message = build_message(data)
        bot.send_message(CHAT_ID, message)
        return jsonify(ok=True, message="Заявку надіслано"), 200
    except Exception as exc:
        print("Telegram send error:", repr(exc))
        return jsonify(ok=False, error="Не вдалося надіслати заявку в Telegram"), 502


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
