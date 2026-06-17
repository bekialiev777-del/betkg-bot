import os
import telebot
from telebot import types

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = telebot.TeleBot(BOT_TOKEN)

user_data = {}
user_state = {}


def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("💸 Пополнить", "💳 Вывести")
    kb.add("👨‍💻 Оператор")
    return kb


def methods_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🏦 МБанк", "📱 О!Деньги")
    kb.add("💎 Оптима", "🏛 Бакай Банк")
    kb.add("⬅️ Назад")
    return kb


def back_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("⬅️ Назад")
    return kb


def delete_user_message(message):
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass


def send_msg(chat_id, text, reply_markup=None):
    return bot.send_message(chat_id, text, reply_markup=reply_markup)


def welcome_text(first_name):
    return f"""👋 Здравствуйте, {first_name}

💎 1xBet KG Premium Service 🇰🇬

⚡ Быстрое пополнение и вывод средств
💸 Без комиссии 0%
🔐 Безопасные и защищённые переводы
🚀 Быстрая обработка заявок

💬 Чат: @betkg
🛟 Поддержка: @betkg

✨ Выберите действие ниже:
"""


@bot.message_handler(commands=["start"])
def start(message):
    delete_user_message(message)

    user_state.pop(message.from_user.id, None)
    user_data.pop(message.from_user.id, None)

    send_msg(message.chat.id, welcome_text(message.from_user.first_name), main_menu())


@bot.message_handler(func=lambda m: m.text == "⬅️ Назад")
def back(message):
    delete_user_message(message)

    user_state.pop(message.from_user.id, None)
    user_data.pop(message.from_user.id, None)

    send_msg(message.chat.id, "⬅️ Вы вернулись в главное меню.", main_menu())


@bot.message_handler(func=lambda m: m.text == "👨‍💻 Оператор")
def operator(message):
    delete_user_message(message)

    send_msg(message.chat.id, "👨‍💻 Оператор: @betkg", main_menu())


@bot.message_handler(func=lambda m: m.text == "💸 Пополнить")
def deposit_start(message):
    delete_user_message(message)

    user_state[message.from_user.id] = "deposit_id"
    user_data[message.from_user.id] = {"type": "Пополнение"}

    send_msg(message.chat.id, "🆔 Напишите ваш ID счёт:", back_menu())


@bot.message_handler(func=lambda m: m.text == "💳 Вывести")
def withdraw_start(message):
    delete_user_message(message)

    user_state[message.from_user.id] = "withdraw_id"
    user_data[message.from_user.id] = {"type": "Вывод"}

    send_msg(message.chat.id, "🆔 Напишите ваш ID счёт:", back_menu())


@bot.message_handler(func=lambda m: True)
def handle_steps(message):
    user_id = message.from_user.id
    state = user_state.get(user_id)

    if not state:
        delete_user_message(message)
        send_msg(message.chat.id, "⚠️ Выберите кнопку из меню.", main_menu())
        return

    if state in ["deposit_id", "withdraw_id"]:
        user_data[user_id]["account_id"] = message.text
        user_state[user_id] = "amount"

        delete_user_message(message)

        send_msg(message.chat.id, "💰 Введите сумму:", back_menu())
        return

    if state == "amount":
        if not message.text.isdigit():
            delete_user_message(message)
            send_msg(message.chat.id, "⚠️ Сумму напишите цифрами.", back_menu())
            return

        user_data[user_id]["amount"] = message.text
        user_state[user_id] = "method"

        delete_user_message(message)

        send_msg(message.chat.id, "🏦 Выберите метод:", methods_menu())
        return

    if state == "method":
        methods = ["🏦 МБанк", "📱 О!Деньги", "💎 Оптима", "🏛 Бакай Банк"]

        if message.text not in methods:
            delete_user_message(message)
            send_msg(message.chat.id, "⚠️ Выберите метод кнопкой.", methods_menu())
            return

        delete_user_message(message)

        data = user_data[user_id]
        username = message.from_user.username or "нет username"

        admin_text = (
            f"📩 Новая заявка\n\n"
            f"📌 Тип: {data['type']}\n"
            f"🆔 ID счёт: {data['account_id']}\n"
            f"💰 Сумма: {data['amount']}\n"
            f"🏦 Метод: {message.text}\n\n"
            f"👤 Telegram ID: {user_id}\n"
            f"📛 Username: @{username}"
        )

        bot.send_message(ADMIN_ID, admin_text)

        send_msg(
            message.chat.id,
            "✅ Заявка отправлена.\n⏳ Ожидайте подтверждения оператора.",
            main_menu()
        )

        user_state.pop(user_id, None)
        user_data.pop(user_id, None)


bot.infinity_polling(skip_pending=True)
