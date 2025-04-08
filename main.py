import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from flask import Flask, request

TOKEN = "7807968065:AAEK3GHMqONr2IGZjNI1Ukv7-0Yq_ZmHXDs"
WEBHOOK_URL = "https://<ВАШ-АДРЕС-RENDER>.onrender.com/webhook"  # ЗАМЕНИ НА СВОЙ

app_flask = Flask(__name__)
application = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Оттарить машину", callback_data='tara')],
        [InlineKeyboardButton("Ввести брутто", callback_data='brutto')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Выберите действие:', reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if query.data == 'tara':
        await query.edit_message_text("Функция тары пока в разработке.")
    elif query.data == 'brutto':
        await query.edit_message_text("Функция брутто пока в разработке.")

@app_flask.route("/webhook", methods=["POST"])
def webhook():
    if application:
        application.update_queue.put(request.json)
    return "ok"

def main():
    global application
    logging.basicConfig(level=logging.INFO)
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.run_webhook(
        listen="0.0.0.0",
        port=8080,
        webhook_url=WEBHOOK_URL,
        allowed_updates=Update.ALL_TYPES,
    )

if __name__ == "__main__":
    from threading import Thread
    import os

    Thread(target=main).start()
    app_flask.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))