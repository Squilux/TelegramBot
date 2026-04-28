from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "8724419661:AAF23AC7PPD71ztkdLlbCxsyzgLHpKtmcOE"
DONATE_URL = "https://www.donationalerts.com/r/bananagrief"

user_data = {}

# ===============================
# ЦЕНЫ
# ===============================

prices_rub = {
    "cases": {
        "Divine": {"1": 49, "5": 199, "10": 349, "20": 599},
        "Inferno": {"1": 59, "5": 249, "10": 449, "20": 799},
        "Supreme": {"1": 69, "5": 299, "10": 549, "20": 999},
        "Titan": {"1": 79, "5": 349, "10": 649, "20": 1199},
        "Galaxy": {"1": 89, "5": 399, "10": 749, "20": 1399},
        "Royal": {"1": 99, "5": 449, "10": 849, "20": 1599},
        "Legend": {"1": 109, "5": 499, "10": 949, "20": 1799},
    },
    "ranks": {
        "VIP": 149,
        "FLY": 199,
        "VIP+": 249,
        "PREMIUM": 399,
        "HELPER": 599,
    },
    "points": {
        "100": 49,
        "300": 99,
        "500": 149,
        "1000": 249,
    },
    "blocks": {
        "100": 29,
        "500": 79,
        "1000": 149,
        "1500": 199,
    }
}

prices_eur = {
    "cases": {
        "Divine": {"1": 0.6, "5": 2.4, "10": 4, "20": 7},
        "Inferno": {"1": 0.7, "5": 2.8, "10": 5, "20": 9},
        "Supreme": {"1": 0.8, "5": 3.2, "10": 6, "20": 11},
        "Titan": {"1": 0.9, "5": 3.6, "10": 7, "20": 13},
        "Galaxy": {"1": 1.0, "5": 4.0, "10": 8, "20": 15},
        "Royal": {"1": 1.1, "5": 4.4, "10": 9, "20": 17},
        "Legend": {"1": 1.2, "5": 4.8, "10": 10, "20": 19},
    },
    "ranks": {
        "VIP": 2,
        "FLY": 3,
        "VIP+": 4,
        "PREMIUM": 6,
        "HELPER": 8,
    },
    "points": {
        "100": 1,
        "300": 2,
        "500": 3,
        "1000": 5,
    },
    "blocks": {
        "100": 1,
        "500": 2,
        "1000": 3,
        "1500": 4,
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

        elif data.get("waiting_nick"):
            nickname = text
            item = data["item"]
            amount = data["amount"]

            if t == "cases":
                price = prices["cases"][item][amount]
                message = f"{nickname} {item} {amount}"
                example = message

            elif t == "points":
                price = prices["points"][item]
                message = f"{nickname} {item}"
                example = message

            elif t == "blocks":
                price = prices["blocks"][item]
                message = f"{nickname} {item}"
                example = message

            elif t == "ranks":
                price = prices["ranks"][item]
                message = f"{nickname} {item}"
                example = message

            url = f"{DONATE_URL}?amount={price}&message={message}"

            keyboard = [[InlineKeyboardButton(f"💳 Оплатить {price}{symbol}", url=url)]]

            await update.message.reply_text(
                f"🛒 Заказ:\n\n"
                f"Ник: {nickname}\n"
                f"{item} x{amount}\n"
                f"Цена: {price}{symbol}\n\n"
                f"⚠️ ВАЖНО:\n"
                f"Укажи в сообщении к донату:\n"
                f"`{example}`",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

            del user_data[user_id]

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