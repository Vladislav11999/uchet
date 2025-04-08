import logging
import threading
import http.server
import socketserver
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Keep-alive HTTP-сервер для Render
def keep_alive():
    PORT = 8080
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("Фейковый сервер запущен на порту", PORT)
        httpd.serve_forever()

threading.Thread(target=keep_alive).start()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = "7807968065:AAEK3GHMqONr2IGZjNI1Ukv7-0Yq_ZmHXDs"

WAIT_TARA_NUMBER, WAIT_TARA_WEIGHT, WAIT_BRUTTO_SELECT, WAIT_BRUTTO_WEIGHT = range(4)
pending_trucks = {}

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Оттарить машину", callback_data='tara')],
        [InlineKeyboardButton("Ввести брутто", callback_data='brutto')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)

async def start_tara(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Введите номер машины:")
    return WAIT_TARA_NUMBER

async def receive_tara_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = update.message.text.strip().upper()
    date_str = datetime.now().strftime("%d.%m.%Y")
    full_number = f"{number} ({date_str})"
    context.user_data['number'] = full_number
    context.user_data['tara_time'] = datetime.now()
    await update.message.reply_text(f"Введите вес тары для {full_number}:")
    return WAIT_TARA_WEIGHT

async def receive_tara_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        tara = int(update.message.text.strip())
        number = context.user_data['number']
        pending_trucks[number] = {
            'tara': tara,
            'tara_time': context.user_data['tara_time']
        }
        await update.message.reply_text(f"Машина {number} оттарена. Тара: {tara}.")
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число.")
        return WAIT_TARA_WEIGHT

async def start_brutto_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    if not pending_trucks:
        await update.callback_query.edit_message_text("Нет оттарированных машин.")
        return ConversationHandler.END

    keyboard = [
        [InlineKeyboardButton(number, callback_data=f"brutto_{number}")]
        for number in pending_trucks.keys()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text("Выберите машину для ввода брутто:", reply_markup=reply_markup)
    return WAIT_BRUTTO_SELECT

async def select_truck_for_brutto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    number = query.data.replace("brutto_", "")
    context.user_data['selected_number'] = number
    await query.edit_message_text(f"Введите брутто для машины {number}:")
    return WAIT_BRUTTO_WEIGHT

async def receive_brutto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        brutto = int(update.message.text.strip())
        number = context.user_data['selected_number']
        tara = pending_trucks[number]['tara']
        tara_time = pending_trucks[number]['tara_time']
        brutto_time = datetime.now()
        diff = brutto_time - tara_time
        netto = brutto - tara
        del pending_trucks[number]
        await update.message.reply_text(
            f"Машина {number}\n"
            f"Тара: {tara}\n"
            f"Брутто: {brutto}\n"
            f"Нетто: {netto}\n"
            f"Время между тарой и брутто: {diff.seconds // 3600}ч {(diff.seconds % 3600) // 60}мин"
        )
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Введите число.")
        return WAIT_BRUTTO_WEIGHT

app = ApplicationBuilder().token(TOKEN).build()

tara_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_tara, pattern="tara")],
    states={
        WAIT_TARA_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_tara_number)],
        WAIT_TARA_WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_tara_weight)],
    },
    fallbacks=[],
)

brutto_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_brutto_selection, pattern="brutto")],
    states={
        WAIT_BRUTTO_SELECT: [CallbackQueryHandler(select_truck_for_brutto, pattern="^brutto_")],
        WAIT_BRUTTO_WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_brutto)],
    },
    fallbacks=[],
)

app.add_handler(tara_conv)
app.add_handler(brutto_conv)
app.add_handler(CommandHandler("start", menu))
app.add_handler(CommandHandler("m", menu))

app.run_polling()