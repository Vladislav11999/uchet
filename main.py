
import logging
import asyncio
import time
import os
import nest_asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

TOKEN = "7807968065:AAEK3GHMqONr2IGZjNI1Ukv7-0Yq_ZmHXDs"
WEBHOOK_URL = "https://uchet.onrender.com"
PORT = int(os.environ.get("PORT", 8080))

nest_asyncio.apply()
user_last_command = {}
machine_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Оттарить", callback_data="tara")],
        [InlineKeyboardButton("Брутто", callback_data="brutto")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "tara":
        await query.edit_message_text("Введите номер и тару через пробел (например: ABC123 7400)")
        context.user_data["mode"] = "tara"
    elif query.data == "brutto":
        await query.edit_message_text("Введите номер и брутто через пробел (например: ABC123 12400)")
        context.user_data["mode"] = "brutto"

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get("mode")
    if not mode:
        return
    parts = update.message.text.strip().split()
    if len(parts) != 2 or not parts[1].isdigit():
        await update.message.reply_text("Неправильный формат. Введите номер и вес через пробел.")
        return
    number, weight = parts[0], int(parts[1])
    if mode == "tara":
        machine_data[number] = {"tara": weight, "timestamp": time.time()}
        await update.message.reply_text(f"Машина {number} оттарена: {weight} кг")
    elif mode == "brutto":
        if number not in machine_data:
            await update.message.reply_text("Сначала введите тару для этой машины.")
            return
        brutto = weight
        tara = machine_data[number]["tara"]
        net = brutto - tara
        delta = int((time.time() - machine_data[number]["timestamp"]) / 60)
        await update.message.reply_text(f"Машина {number}:
Брутто: {brutto} кг
Тара: {tara} кг
Нетто: {net} кг
Прошло: {delta} мин.")

async def run_bot():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    await app.bot.delete_webhook()
    await app.bot.set_webhook(WEBHOOK_URL + "/webhook")
    logging.info(f"Webhook установлен: {WEBHOOK_URL}/webhook")

    await app.run_webhook(listen="0.0.0.0", port=PORT, webhook_url=WEBHOOK_URL + "/webhook")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(run_bot())
