import logging
import threading
import http.server
import socketserver
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Фейковый веб-сервер для Render
def keep_alive():
    PORT = 8080
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("Сервер запущен на порту", PORT)
        httpd.serve_forever()

threading.Thread(target=keep_alive).start()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = "7807968065:AAEK3GHMqONr2IGZjNI1Ukv7-0Yq_ZmHXDs"

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
        await query.edit_message_text(text="Функция тары пока в разработке.")
    elif query.data == 'brutto':
        await query.edit_message_text(text="Функция брутто пока в разработке.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()

if __name__ == '__main__':
    main()