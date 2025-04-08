from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from collections import defaultdict
from datetime import datetime

TOKEN = 'ВАШ_ТОКЕН_ЗДЕСЬ'

# Состояния
WAIT_NUMBER, WAIT_TARA, WAIT_BRUTTO_SELECT, WAIT_BRUTTO_INPUT = range(4)
pending_trucks = {}

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Оттарить машину", callback_data='start_tara')],
        [InlineKeyboardButton("Ввести брутто", callback_data='select_brutto')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)

async def start_tara_entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Введите номер машины:")
    return WAIT_NUMBER

async def receive_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    now = datetime.now()
    date_str = now.strftime("%d.%m.%Y")
    number = update.message.text.strip().upper()
    full_number = f"{number} ({date_str})"
    context.user_data['number'] = full_number
    context.user_data['tara_time'] = now
    await update.message.reply_text(f"Введите вес тары для машины {full_number}:")
    return WAIT_TARA

async def receive_tara(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        tara = int(update.message.text.strip())
        number = context.user_data['number']
        tara_time = context.user_data['tara_time']
        pending_trucks[number] = {'tara': tara, 'tara_time': tara_time}
        await update.message.reply_text(f"Машина {number} оттарена. Тара: {tara}.")
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Введите корректное число для тары.")
        return WAIT_TARA

async def start_brutto_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    if not pending_trucks:
        await update.callback_query.edit_message_text("Нет оттарированных машин.")
        return ConversationHandler.END

    keyboard = [
        [InlineKeyboardButton(number, callback_data=f'brutto_{number}')]
        for number in pending_trucks.keys()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text("Выберите машину для ввода брутто:", reply_markup=reply_markup)
    return WAIT_BRUTTO_SELECT

async def select_truck(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    number = query.data.replace('brutto_', '')
    context.user_data['selected_number'] = number
    await query.edit_message_text(text=f"Введите брутто для машины {number}:")
    return WAIT_BRUTTO_INPUT

async def receive_brutto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        brutto = int(update.message.text.strip())
        number = context.user_data['selected_number']
        tara = pending_trucks[number]['tara']
        tara_time = pending_trucks[number]['tara_time']
        brutto_time = datetime.now()
        time_diff = brutto_time - tara_time
        hours, remainder = divmod(time_diff.total_seconds(), 3600)
        minutes = remainder // 60

        netto = brutto - tara

        response = (
            f"Машина {number}\n"
            f"Тара: {tara}\n"
            f"Брутто: {brutto}\n"
            f"Нетто: {netto}\n"
            f"Время между тарой и брутто: {int(hours)}ч {int(minutes)}мин"
        )
        del pending_trucks[number]
        await update.message.reply_text(response)
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Введите корректное число для брутто.")
        return WAIT_BRUTTO_INPUT

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Операция отменена.")
    return ConversationHandler.END

app = ApplicationBuilder().token(TOKEN).build()

# Обработчики
conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_tara_entry, pattern="start_tara")],
    states={
        WAIT_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_number)],
        WAIT_TARA: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_tara)],
        WAIT_BRUTTO_SELECT: [CallbackQueryHandler(select_truck, pattern="^brutto_")],
        WAIT_BRUTTO_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_brutto)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

app.add_handler(conv_handler)
app.add_handler(CommandHandler("m", menu))
app.add_handler(CallbackQueryHandler(start_brutto_selection, pattern="select_brutto"))

app.run_polling()