import json
import os
import nest_asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, ConversationHandler, filters
)

nest_asyncio.apply()

DATA_FILE = 'data.json'
ADMIN_ID = [1234714307, 6000661816]  # Список админов

# Состояния для ConversationHandler
TRACK, DESC, TIME = range(3)
CHANGE_TRACK, CHANGE_FIELD, CHANGE_VALUE = range(3, 6)


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


# --- Команды ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Введи трек-номер, чтобы получить информацию.\n"
        "Админ-команды: /add /change /delete /list"
    )


# --- ADD ---

async def add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in ADMIN_ID:
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
    await update.message.reply_text("Введите примерное время доставки:")
    return TIME


async def add_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['time'] = update.message.text.strip()
    data = load_data()
    track = context.user_data['track']
    data[track] = {
        'description': context.user_data['desc'],
        'delivery_time': context.user_data['time'],
        'status': "В пути"
    }
    save_data(data)
    await update.message.reply_text(f"Данные по треку {track} сохранены.")
    return ConversationHandler.END


# --- CHANGE ---

async def change_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in ADMIN_ID:
        await update.message.reply_text("Только админ может изменять данные.")
        return ConversationHandler.END
    await update.message.reply_text("Введите трек-номер для изменения:")
    return CHANGE_TRACK


async def change_track(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track = update.message.text.strip()
    data = load_data()
    if track not in data:
        await update.message.reply_text("Такого трек-номера нет.")
        return ConversationHandler.END
    context.user_data['track'] = track
    await update.message.reply_text("Что изменить? (description/delivery_time/status)")
    return CHANGE_FIELD


async def change_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    field = update.message.text.strip()
    if field not in ["description", "delivery_time", "status"]:
        await update.message.reply_text("Неверное поле.")
        return ConversationHandler.END
    context.user_data['field'] = field
    await update.message.reply_text(f"Введите новое значение для {field}:")
    return CHANGE_VALUE


async def change_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    value = update.message.text.strip()
    data = load_data()
    data[context.user_data['track']][context.user_data['field']] = value
    save_data(data)
    await update.message.reply_text("Данные успешно изменены.")
    return ConversationHandler.END


# --- DELETE ---

async def delete_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in ADMIN_ID:
        await update.message.reply_text("Только админ может удалять данные.")
        return
    args = context.args
    if not args:
        await update.message.reply_text("Использование: /delete <трек-номер>")
        return
    track = args[0]
    data = load_data()
    if track in data:
        del data[track]
        save_data(data)
        await update.message.reply_text(f"Трек {track} удалён.")
    else:
        await update.message.reply_text("Трек не найден.")


# --- LIST ---

async def list_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    if not data:
        await update.message.reply_text("Нет данных.")
        return
    reply = "\n".join([f"{t}: {info['description']} ({info['status']})" for t, info in data.items()])
    await update.message.reply_text(reply)


# --- GET INFO ---

async def get_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track = update.message.text.strip()
    data = load_data()
    if track in data:
        info = data[track]
        reply = (
            f"Трек: {track}\n"
            f"Описание: {info['description']}\n"
            f"Время доставки: {info['delivery_time']}\n"
            f"Статус: {info['status']}"
        )
    else:
        reply = "Информация не найдена."
    await update.message.reply_text(reply)


# ---
