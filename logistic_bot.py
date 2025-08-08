import json
import os
import nest_asyncio

from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, ConversationHandler, filters
)

nest_asyncio.apply()  # Чтобы не было ошибки с event loop

DATA_FILE = 'data.json'
ADMIN_ID = 1234714307  # Твой Telegram ID

TRACK, DESC, TIME = range(3)

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Введи трек-номер, чтобы получить информацию о товаре.\n"
        "Если ты админ, используй команду /add, чтобы добавить новый трек."
    )

async def add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("Извини, только админ может добавлять данные.")
        return ConversationHandler.END
    await update.message.reply_text("Введите трек-номер:")
    return TRACK

async def add_track(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['track'] = update.message.text.strip()
    await update.message.reply_text("Введите описание товара:")
    return DESC

async def add_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['desc'] = update.message.text.strip()
    await update.message.reply_text("Введите примерное время доставки (например, 3 дня):")
    return TIME

async def add_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['time'] = update.message.text.strip()

    data = load_data()
    track = context.user_data['track']
    data[track] = {
        'description': context.user_data['desc'],
        'delivery_time': context.user_data['time']
    }
    save_data(data)

    await update.message.reply_text(f"Данные по трек-номеру {track} успешно сохранены.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Операция отменена.")
    return ConversationHandler.END

async def get_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track = update.message.text.strip()
    data = load_data()
    if track in data:
        info = data[track]
        reply = (
            f"Информация по трек-номеру {track}:\n"
            f"Описание: {info['description']}\n"
            f"Примерное время доставки: {info['delivery_time']}"
        )
    else:
        reply = "Информация по такому трек-номеру не найдена."
    await update.message.reply_text(reply)

async def main():
    TOKEN = "7706163791:AAE5QCgERjJRAtvqWtH4ZysiGgk4VPG3p7o"
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('add', add_start)],
        states={
            TRACK: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_track)],
            DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_desc)],
            TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_time)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_info))

    print("Бот запущен...")
    await app.run_polling()

if __name__ == '__main__':
    import asyncio
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())
