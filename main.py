import asyncio
import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import nest_asyncio

nest_asyncio.apply()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем токен бота и URL вебхука из переменных окружения
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL", "https://uchet.onrender.com")
PORT = int(os.environ.get("PORT", 10000))

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Бот запущен и работает!")

# Основная функция запуска бота
async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    webhook_path = "/webhook"

    await app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=webhook_path,
        webhook_url=f"{WEBHOOK_URL}{webhook_path}"
    )

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
