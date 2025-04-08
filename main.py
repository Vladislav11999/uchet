import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "7807968065:AAEK3GHMqONr2IGZjNI1Ukv7-0Yq_ZmHXDs"
WEBHOOK_URL = "https://uchet.onrender.com/webhook"
PORT = 8080

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Оттарить машину", callback_data="tara")],
        [InlineKeyboardButton("Ввести брутто", callback_data="brutto")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "tara":
        await query.edit_message_text("Функция тары пока в разработке.")
    elif query.data == "brutto":
        await query.edit_message_text("Функция брутто пока в разработке.")

async def main():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))

    await app.bot.delete_webhook()
    await app.bot.set_webhook(WEBHOOK_URL)
    await app.run_webhook(listen="0.0.0.0", port=PORT, webhook_url=WEBHOOK_URL)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())