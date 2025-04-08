
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import datetime

TOKEN = "7807968065:AAEK3GHMqONr2IGZjNI1Ukv7-0Yq_ZmHXDs"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['Поставить машину', 'Завершить смену'], ['Показать все машины', 'Посчитать брутто']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text('Привет! Я бот для учёта. Выберите действие:', reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == 'Поставить машину':
        await update.message.reply_text("Введите номер машины:")
    elif text == 'Завершить смену':
        await update.message.reply_text("Смена завершена.")
    elif text == 'Показать все машины':
        await update.message.reply_text("Пока что список пуст.")
    elif text == 'Посчитать брутто':
        await update.message.reply_text("Функция расчёта брутто в разработке.")
    else:
        await update.message.reply_text(f"Вы ввели: {text}")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
