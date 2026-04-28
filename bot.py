from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

import os
TOKEN = os.getenv("TOKEN")
DONATE_URL = "https://www.donationalerts.com/r/bananagrief"

user_data = {}

# ===============================
# ЦЕНЫ
# ===============================

prices_rub = {
    "cases": {
        "Divine": {"1": 85, "5": 320, "10": 560, "20": 830},
        "Inferno": {"1": 72, "5": 240, "10": 430, "20": 670},
        "Supreme": {"1": 65, "5": 195, "10": 385, "20": 590},
        "Titan": {"1": 58, "5": 175, "10": 265, "20": 490},
        "Galaxy": {"1": 44, "5": 145, "10": 220, "20": 365},
        "Royal": {"1": 35, "5": 115, "10": 155, "20": 285},
        "Legend": {"1": 20, "5": 85, "10": 110, "20": 195},
    },
    "ranks": {
        "VIP": 130,
        "FLY": 99,
        "VIP+": 275,
        "PREMIUM": 440,
        "HELPER": 800,
    },
    "points": {
        "100": 65,
        "300": 130,
        "500": 195,
        "1000": 255,
    },
    "blocks": {
        "100": 50,
        "500": 130,
        "1000": 195,
        "1500": 255,
    }
}

prices_eur = {
    "cases": {
        "Divine": {"1": 0.9, "5": 3.0, "10": 5.5, "20": 8.0},
        "Inferno": {"1": 0.8, "5": 2.7, "10": 5, "20": 7.5},
        "Supreme": {"1": 0.7, "5": 2.0, "10": 4.75, "20": 6.5},
        "Titan": {"1": 0.6, "5": 1.8, "10": 4.0, "20": 5.8},
        "Galaxy": {"1": 0.5, "5": 1.5, "10": 3.5, "20": 5.3},
        "Royal": {"1": 0.4, "5": 1.2, "10": 3.25, "20": 4.8},
        "Legend": {"1": 0.3, "5": 1.0, "10": 3, "20": 4.2},
    },
    "ranks": {
        "VIP": 2.5,
        "FLY": 3,
        "VIP+": 4,
        "PREMIUM": 6,
        "HELPER": 8,
    },
    "points": {
        "100": 1.5,
        "300": 3,
        "500": 5,
        "1000": 8,
    },
    "blocks": {
        "100": 2,
        "500": 3.5,
        "1000": 5.5,
        "1500": 6.75,
    }
}

# ===============================
# START
# ===============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["🇷🇺 RUB", "🇪🇺 EUR"]]
    await update.message.reply_text("💱 Выберите валюту:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

# ===============================
# MENU
# ===============================
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # ВЫБОР ВАЛЮТЫ
    if text in ["🇷🇺 RUB", "🇪🇺 EUR"]:
        user_data[user_id] = {"currency": text}
        keyboard = [
            ["🎰 Кейсы"],
            ["👑 Привилегии"],
            ["💎 Points"],
            ["🏡 Блоки привата"],
            ["⬅️ Назад"]
        ]
        await update.message.reply_text("Выберите раздел:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

    # ВВОД НИКА (САМЫЙ ВАЖНЫЙ БЛОК)
    elif user_id in user_data and user_data[user_id].get("waiting_nick"):
        data = user_data[user_id]

        nickname = text
        item = data["item"]
        amount = data["amount"]
        t = data["type"]

        currency = data["currency"]
        prices = prices_rub if "RUB" in currency else prices_eur
        symbol = "₽" if "RUB" in currency else "€"

        if t == "cases":
            price = prices["cases"][item][amount]
            message = f"{nickname} {item} {amount}"
            example = message
            item_text = f"{item} x{amount}"

        elif t == "points":
            price = prices["points"][item]
            message = f"{nickname} points {item}"
            example = message
            item_text = item

        elif t == "blocks":
            price = prices["blocks"][item]
            message = f"{nickname} acb {item}"
            example = message
            item_text = item

        elif t == "ranks":
            price = prices["ranks"][item]
            message = f"{nickname} {item.lower()}"
            example = message
            item_text = item

        url = f"{DONATE_URL}?amount={price}&message={message}"
        keyboard = [[InlineKeyboardButton(f"💳 Оплатить {price}{symbol}", url=url)]]

        await update.message.reply_text(
            f"🛒 Заказ:\n\n"
            f"Ник: {nickname}\n"
            f"{item_text}\n"
            f"Цена: {price}{symbol}\n\n"
            f"⚠️ ВАЖНО:\n"
            f"Укажи в сообщении к донату:\n"
            f"`{example}`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        del user_data[user_id]

    # МЕНЮ
    elif text == "👑 Привилегии":
        user_data.setdefault(user_id, {})["type"] = "ranks"
        keyboard = [["VIP", "FLY"], ["VIP+", "PREMIUM"], ["HELPER"], ["⬅️ Назад"]]
        await update.message.reply_text("Выберите привилегию:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

    elif text == "🎰 Кейсы":
        user_data.setdefault(user_id, {})["type"] = "cases"
        keyboard = [
            ["Divine", "Inferno"],
            ["Supreme", "Titan"],
            ["Galaxy", "Royal"],
            ["Legend"],
            ["⬅️ Назад"]
        ]
        await update.message.reply_text("Выберите кейс:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

    elif text == "💎 Points":
        user_data.setdefault(user_id, {})["type"] = "points"
        keyboard = [["100", "300"], ["500", "1000"], ["⬅️ Назад"]]
        await update.message.reply_text("Выберите Points:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

    elif text == "🏡 Блоки привата":
        user_data.setdefault(user_id, {})["type"] = "blocks"
        keyboard = [["100", "500"], ["1000", "1500"], ["⬅️ Назад"]]
        await update.message.reply_text("Выберите блоки:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

    elif user_id in user_data:
        data = user_data[user_id]
        currency = data["currency"]
        prices = prices_rub if "RUB" in currency else prices_eur
        symbol = "₽" if "RUB" in currency else "€"

        t = data.get("type")

        if t == "cases" and text in prices["cases"]:
            data["item"] = text
            p = prices["cases"][text]

            keyboard = [
                [f"1 ({p['1']}{symbol})", f"5 ({p['5']}{symbol})"],
                [f"10 ({p['10']}{symbol})", f"20 ({p['20']}{symbol})"],
                ["⬅️ Назад"]
            ]
            await update.message.reply_text("Выберите количество:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

        elif t == "cases" and any(text.startswith(x) for x in ["1", "5", "10", "20"]):
            data["amount"] = text.split(" ")[0]
            data["waiting_nick"] = True
            await update.message.reply_text("Введите ник:")

        elif t in ["ranks", "points", "blocks"] and text in prices[t]:
            data["item"] = text
            data["amount"] = text
            data["waiting_nick"] = True
            await update.message.reply_text("Введите ник:")

    elif text == "⬅️ Назад":
        await start(update, context)

# ===============================
# RUN
# ===============================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu))

print("Бот запущен...")
app.run_polling()
