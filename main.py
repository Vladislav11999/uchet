import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "your_token_here"  # Используется переменная окружения в реальном проекте

logging.basicConfig(level=logging.INFO)

# Клавиатура
main_keyboard = [
    ["🚛 Поставить машину", "🏁 Завершить смену"],
    ["📋 Показать все машины", "⚖️ Посчитать брутто"]
]
reply_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Выберите действие:", reply_markup=reply_markup)

# Обработчики кнопок
async def start_loading(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Начинаем постановку машины!")

async def end_shift(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Смена завершена.")

async def show_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Вот все машины:")

async def calc_brutto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите данные для расчёта брутто.")

# Запуск бота
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^🚛 Поставить машину$"), start_loading))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^🏁 Завершить смену$"), end_shift))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^📋 Показать все машины$"), show_all))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^⚖️ Посчитать брутто$"), calc_brutto))

    app.run_polling()

if __name__ == "__main__":
    main()
