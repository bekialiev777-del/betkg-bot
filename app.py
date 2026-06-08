    import os
import telebot
from telebot import types

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = telebot.TeleBot(BOT_TOKEN)

user_data = {}
user_state = {}
last_bot_message = {}


def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("Пополнить", "Вывести")
    kb.add("Оператор")
    return kb


def methods_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("МБанк", "О!Деньги")
    kb.add("Оптима", "Бакай Банк")
    kb.add("⬅️ Назад")
    return kb


def back_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("⬅️ Назад")
    return kb


def send_clean(chat_id, text, reply_markup=None):
    if chat_id in last_bot_message:
        try:
            bot.delete_message(chat_id, last_bot_message[chat_id])
        except Exception:
            pass

    msg = bot.send_message(chat_id, text, reply_markup=reply_markup)
    last_bot_message[chat_id] = msg.message_id
    return msg


def welcome_text(first_name):
    return f"""Здравствуйте, {first_name} ⚡

1xBet KG — удобный сервис для пополнения и вывода средств без комиссии в Кыргызстане 🇰🇬

🔒 Безопасные и защищённые транзакции
⚡ Быстрая обработка заявок

💬 Наш чат: @betkg

Служба поддержки: @betkg
"""


@bot.message_handler(commands=["start"])
def start(message):
    user_state.pop(message.from_user.id, None)
    user_data.pop(message.from_user.id, None)

    send_clean(
        message.chat.id,
        welcome_text(message.from_user.first_name),
        reply_markup=main_menu()
    )


@bot.message_handler(func=lambda m: m.text == "⬅️ Назад")
def back(message):
    user_state.pop(message.from_user.id, None)
    user_data.pop(message.from_user.id, None)

    send_clean(
        message.chat.id,
        welcome_text(message.from_user.first_name),
        reply_markup=main_menu()
    )


@bot.message_handler(func=lambda m: m.text == "Оператор")
def operator(message):
    send_clean(
        message.chat.id,
        "Оператор: @betkg",
        reply_markup=main_menu()
    )


@bot.message_handler(func=lambda m: m.text == "Пополнить")
def deposit_start(message):
    user_state[message.from_user.id] = "deposit_id"
    user_data[message.from_user.id] = {"type": "Пополнение"}

    send_clean(
        message.chat.id,
        "Напишите ваш ID счёт:",
        reply_markup=back_menu()
    )


@bot.message_handler(func=lambda m: m.text == "Вывести")
def withdraw_start(message):
    user_state[message.from_user.id] = "withdraw_id"
    user_data[message.from_user.id] = {"type": "Вывод"}

    send_clean(
        message.chat.id,
        "Напишите ваш ID счёт:",
        reply_markup=back_menu()
    )


@bot.message_handler(func=lambda m: True)
def handle_steps(message):
    user_id = message.from_user.id
    state = user_state.get(user_id)

    if not state:
        send_clean(
            message.chat.id,
            "Выберите кнопку из меню.",
            reply_markup=main_menu()
        )
        return

    if state in ["deposit_id", "withdraw_id"]:
        user_data[user_id]["account_id"] = message.text
        user_state[user_id] = "amount"

        send_clean(
            message.chat.id,
            "Введите сумму:",
            reply_markup=back_menu()
        )
        return

    if state == "amount":
        if not message.text.isdigit():
            send_clean(
                message.chat.id,
                "Сумму напишите цифрами.",
                reply_markup=back_menu()
            )
            return

        user_data[user_id]["amount"] = message.text
        user_state[user_id] = "method"

        send_clean(
            message.chat.id,
            "Выберите метод:",
            reply_markup=methods_menu()
        )
        return

    if state == "method":
        methods = ["МБанк", "О!Деньги", "Оптима", "Бакай Банк"]

        if message.text not in methods:
            send_clean(
                message.chat.id,
                "Выберите метод кнопкой.",
                reply_markup=methods_menu()
            )
            return

        data = user_data[user_id]
        username = message.from_user.username or "нет username"

        admin_text = (
            f"📩 Новая заявка\n\n"
            f"Тип: {data['type']}\n"
            f"ID счёт: {data['account_id']}\n"
            f"Сумма: {data['amount']}\n"
            f"Метод: {message.text}\n\n"
            f"Telegram ID: {user_id}\n"
            f"Username: @{username}"
        )

        bot.send_message(ADMIN_ID, admin_text)

        send_clean(
            message.chat.id,
            "Заявка отправлена. Ожидайте.",
            reply_markup=main_menu()
        )

        user_state.pop(user_id, None)
        user_data.pop(user_id, None)


bot.infinity_polling(skip_pending=True)
