from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

import os

TOKEN = os.getenv("TOKEN")

DONATE_URL = "https://www.donationalerts.com/r/bananagrief"

user_data = {}

# ===============================
# ЦЕНЫ
# ===============================

prices_rub = {
    "cases": {
        "Divine": {"1": 49, "5": 199, "10": 369, "20": 699},
        "Inferno": {"1": 35, "5": 149, "10": 279, "20": 529},
        "Supreme": {"1": 39, "5": 169, "10": 319, "20": 599},
        "Bloodmoon": {"1": 79, "5": 349, "10": 649, "20": 1199},
        "Galaxy": {"1": 59, "5": 259, "10": 479, "20": 899},
        "Ragnarok": {"1": 89, "5": 399, "10": 749, "20": 1399},
        "Legend": {"1": 19, "5": 79, "10": 279, "20": 485},
    },
    "ranks": {
        "VIP": 130,
        "FLY": 99,
        "VIP+": 275,
        "PREMIUM": 440,
        "HELPER": 800,
    },
    "points": {
        "1000": 250,
        "1500": 400,
        "2000": 550,
        "2500": 680,
        "5000": 999,
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
        "Divine": {"1": 0.35, "5": 1.49, "10": 2.99, "20": 5.49},
        "Inferno": {"1": 0.25, "5": 1.09, "10": 1.99, "20": 3.99},
        "Supreme": {"1": 0.29, "5": 1.29, "10": 2.49, "20": 4.69},
        "Bloodmoon": {"1": 0.59, "5": 2.49, "10": 4.49, "20": 7.99},
        "Galaxy": {"1": 0.45, "5": 1.99, "10": 3.69, "20": 6.49},
        "Ragnarok": {"1": 0.69, "5": 2.99, "10": 5.49, "20": 9.99},
        "Legend": {"1": 0.19, "5": 0.79, "10": 1.49, "20": 2.99},
    },
    "ranks": {
        "VIP": 2.5,
        "FLY": 3,
        "VIP+": 4,
        "PREMIUM": 6,
        "HELPER": 8,
    },
    "points": {
        "1000": 2.5,
        "1500": 4,
        "2000": 5.5,
        "2500": 6,
        "5000": 8.5,
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

    await update.message.reply_text(
        "💱 Выберите валюту:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )
    )

# ===============================
# MAIN MENU
# ===============================

async def show_main_menu(update: Update):
    keyboard = [
        ["🎰 Кейсы"],
        ["👑 Привилегии"],
        ["💎 Points"],
        ["🏡 Блоки привата"],
        ["⬅️ Назад"]
    ]

    await update.message.reply_text(
        "Выберите раздел:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )
    )

# ===============================
# MENU
# ===============================

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # ===============================
    # BACK BUTTON
    # ===============================

    if text == "⬅️ Назад":
        currency = user_data.get(user_id, {}).get("currency")

        # Если валюта выбрана — возвращаем в меню
        if currency:
            user_data[user_id] = {"currency": currency}
            await show_main_menu(update)

        # Если валюты нет — на старт
        else:
            await start(update, context)

        return

    # ===============================
    # ВЫБОР ВАЛЮТЫ
    # ===============================

    if text in ["🇷🇺 RUB", "🇪🇺 EUR"]:
        user_data[user_id] = {"currency": text}
        await show_main_menu(update)

    # ===============================
    # ВВОД НИКА
    # ===============================

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

        keyboard = [[
            InlineKeyboardButton(
                f"💳 Оплатить {price}{symbol}",
                url=url
            )
        ]]

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

    # ===============================
    # МЕНЮ
    # ===============================

    elif text == "👑 Привилегии":
        user_data.setdefault(user_id, {})["type"] = "ranks"

        keyboard = [
            ["VIP", "FLY"],
            ["VIP+", "PREMIUM"],
            ["HELPER"],
            ["⬅️ Назад"]
        ]

        await update.message.reply_text(
            "Выберите привилегию:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True
            )
        )

    elif text == "🎰 Кейсы":
        user_data.setdefault(user_id, {})["type"] = "cases"

        keyboard = [
            ["Divine", "Inferno"],
            ["Supreme", "Bloodmoon"],
            ["Galaxy", "Ragnarok"],
            ["Legend"],
            ["⬅️ Назад"]
        ]

        await update.message.reply_text(
            "Выберите кейс:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True
            )
        )

    elif text == "💎 Points":
        user_data.setdefault(user_id, {})["type"] = "points"

        keyboard = [
            ["1000", "1500"],
            ["2000", "2500", "5000"],
            ["⬅️ Назад"]
        ]

        await update.message.reply_text(
            "Выберите Points:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True
            )
        )

    elif text == "🏡 Блоки привата":
        user_data.setdefault(user_id, {})["type"] = "blocks"

        keyboard = [
            ["100", "500"],
            ["1000", "1500"],
            ["⬅️ Назад"]
        ]

        await update.message.reply_text(
            "Выберите блоки:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True
            )
        )

    # ===============================
    # ОБРАБОТКА ВЫБОРА
    # ===============================

    elif user_id in user_data:
        data = user_data[user_id]

        currency = data["currency"]

        prices = prices_rub if "RUB" in currency else prices_eur
        symbol = "₽" if "RUB" in currency else "€"

        t = data.get("type")

        # ===============================
        # CASES
        # ===============================

        if t == "cases" and text in prices["cases"]:
            data["item"] = text

            p = prices["cases"][text]

            keyboard = [
                [f"1 ({p['1']}{symbol})", f"5 ({p['5']}{symbol})"],
                [f"10 ({p['10']}{symbol})", f"20 ({p['20']}{symbol})"],
                ["⬅️ Назад"]
            ]

            await update.message.reply_text(
                "Выберите количество:",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard,
                    resize_keyboard=True
                )
            )

        elif t == "cases" and any(
            text.startswith(x) for x in ["1", "5", "10", "20"]
        ):
            data["amount"] = text.split(" ")[0]
            data["waiting_nick"] = True

            await update.message.reply_text("Введите ник:")

        # ===============================
        # OTHER ITEMS
        # ===============================

        elif t in ["ranks", "points", "blocks"] and text in prices[t]:
            data["item"] = text
            data["amount"] = text
            data["waiting_nick"] = True

            await update.message.reply_text("Введите ник:")

# ===============================
# RUN
# ===============================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu))

print("Бот запущен...")

app.run_polling()    },
    "ranks": {
        "VIP": 130,
        "FLY": 99,
        "VIP+": 275,
        "PREMIUM": 440,
        "HELPER": 800,
    },
    "points": {
        "1000": 250,
        "1500": 400,
        "2000": 550,
        "2500": 680,
        "5000": 999,
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
        "Divine": {"1": 0.35, "5": 1.49, "10": 2.99, "20": 5.49},
        "Inferno": {"1": 0.25, "5": 1.09, "10": 1.99, "20": 3.99},
        "Supreme": {"1": 0.29, "5": 1.29, "10": 2.49, "20": 4.69},
        "Bloodmoon": {"1": 0.59, "5": 2.49, "10": 4.49, "20": 7.99},
        "Galaxy": {"1": 0.45, "5": 1.99, "10": 3.69, "20": 6.49},
        "Ragnarok": {"1": 0.69, "5": 2.99, "10": 5.49, "20": 9.99},
        "Legend": {"1": 0.19, "5": 0.79, "10": 1.49, "20": 2.99},
    },
    "ranks": {
        "VIP": 2.5,
        "FLY": 3,
        "VIP+": 4,
        "PREMIUM": 6,
        "HELPER": 8,
    },
    "points": {
        "1000": 2.5,
        "1500": 4,
        "2000": 5.5,
        "2500": 6,
        "5000": 8.5,
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

    await update.message.reply_text(
        "💱 Выберите валюту:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )
    )

# ===============================
# MAIN MENU
# ===============================

async def show_main_menu(update: Update):
    keyboard = [
        ["🎰 Кейсы"],
        ["👑 Привилегии"],
        ["💎 Points"],
        ["🏡 Блоки привата"],
        ["⬅️ Назад"]
    ]

    await update.message.reply_text(
        "Выберите раздел:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )
    )

# ===============================
# MENU
# ===============================

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # ===============================
    # BACK BUTTON
    # ===============================

    if text == "⬅️ Назад":
        currency = user_data.get(user_id, {}).get("currency")

        # Если валюта выбрана — возвращаем в меню
        if currency:
            user_data[user_id] = {"currency": currency}
            await show_main_menu(update)

        # Если валюты нет — на старт
        else:
            await start(update, context)

        return

    # ===============================
    # ВЫБОР ВАЛЮТЫ
    # ===============================

    if text in ["🇷🇺 RUB", "🇪🇺 EUR"]:
        user_data[user_id] = {"currency": text}
        await show_main_menu(update)

    # ===============================
    # ВВОД НИКА
    # ===============================

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

        keyboard = [[
            InlineKeyboardButton(
                f"💳 Оплатить {price}{symbol}",
                url=url
            )
        ]]

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

    # ===============================
    # МЕНЮ
    # ===============================

    elif text == "👑 Привилегии":
        user_data.setdefault(user_id, {})["type"] = "ranks"

        keyboard = [
            ["VIP", "FLY"],
            ["VIP+", "PREMIUM"],
            ["HELPER"],
            ["⬅️ Назад"]
        ]

        await update.message.reply_text(
            "Выберите привилегию:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True
            )
        )

    elif text == "🎰 Кейсы":
        user_data.setdefault(user_id, {})["type"] = "cases"

        keyboard = [
            ["Divine", "Inferno"],
            ["Supreme", "Bloodmoon"],
            ["Galaxy", "Ragnarok"],
            ["Legend"],
            ["⬅️ Назад"]
        ]

        await update.message.reply_text(
            "Выберите кейс:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True
            )
        )

    elif text == "💎 Points":
        user_data.setdefault(user_id, {})["type"] = "points"

        keyboard = [
            ["1000", "1500"],
            ["2000", "2500", "5000"],
            ["⬅️ Назад"]
        ]

        await update.message.reply_text(
            "Выберите Points:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True
            )
        )

    elif text == "🏡 Блоки привата":
        user_data.setdefault(user_id, {})["type"] = "blocks"

        keyboard = [
            ["100", "500"],
            ["1000", "1500"],
            ["⬅️ Назад"]
        ]

        await update.message.reply_text(
            "Выберите блоки:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True
            )
        )

    # ===============================
    # ОБРАБОТКА ВЫБОРА
    # ===============================

    elif user_id in user_data:
        data = user_data[user_id]

        currency = data["currency"]

        prices = prices_rub if "RUB" in currency else prices_eur
        symbol = "₽" if "RUB" in currency else "€"

        t = data.get("type")

        # ===============================
        # CASES
        # ===============================

        if t == "cases" and text in prices["cases"]:
            data["item"] = text

            p = prices["cases"][text]

            keyboard = [
                [f"1 ({p['1']}{symbol})", f"5 ({p['5']}{symbol})"],
                [f"10 ({p['10']}{symbol})", f"20 ({p['20']}{symbol})"],
                ["⬅️ Назад"]
            ]

            await update.message.reply_text(
                "Выберите количество:",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard,
                    resize_keyboard=True
                )
            )

        elif t == "cases" and any(
            text.startswith(x) for x in ["1", "5", "10", "20"]
        ):
            data["amount"] = text.split(" ")[0]
            data["waiting_nick"] = True

            await update.message.reply_text("Введите ник:")

        # ===============================
        # OTHER ITEMS
        # ===============================

        elif t in ["ranks", "points", "blocks"] and text in prices[t]:
            data["item"] = text
            data["amount"] = text
            data["waiting_nick"] = True

            await update.message.reply_text("Введите ник:")

# ===============================
# RUN
# ===============================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu))

print("Бот запущен...")

app.run_polling()
