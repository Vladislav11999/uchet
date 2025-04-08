
import logging
import asyncio
import nest_asyncio
import time
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "7807968065:AAEK3GHMqONr2IGZjNI1Ukv7-0Yq_ZmHXDs"
WEBHOOK_URL = "https://uchet.onrender.com/webhook"
PORT = int(os.environ.get("PORT", 8080))

nest_asyncio.apply()

# Храним последнее время команды от каждого пользователя
user_last_command = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    now = time.time()
    last_time = user_last_command.get(user_id, 0)

    if now - last_time < 5:  # 5 секунд защита от спама
        logging.info(f"Flood protection: user {user_id} слишком быстро вызвал /start")
        return

    user_last_command[user_id] = now

    logging.info(f"/start от пользователя: {user_id} ({update.effective_user.username})")

    keyboard = [
        [InlineKeyboardButton("Оттарить машину", callback_data="tara")],
        [InlineKeyboardButton("Ввести брутто", callback_data="brutto")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    logging.info(f"Кнопка нажата: {query.data} от {query.from_user.id} ({query.from_user.username})")

    if query.data == "tara":
        await query.edit_message_text("Функция тары пока в разработке.")
    elif query.data == "brutto":
        await query.edit_message_text("Функция брутто пока в разработке.")

async def run_bot():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))

    await app.bot.delete_webhook()
    await app.bot.set_webhook(WEBHOOK_URL)
    await app.run_webhook(listen="0.0.0.0", port=PORT, webhook_url=WEBHOOK_URL)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(run_bot())
