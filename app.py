import telebot
from telebot import types

BOT_TOKEN = "8992012913:AAGaED5idyrmi2FdNqw1FaBs7b135c6cbyA"
ADMIN_ID = 7845631391

bot = telebot.TeleBot(BOT_TOKEN)

balances = {}
amounts = {}

def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("💳 Пополнение", "👤 Баланс")
    kb.add("💸 Вывод", "📞 Поддержка")
    return kb

@bot.message_handler(commands=["start"])
def start(message):
    balances.setdefault(message.from_user.id, 0)

    username = message.from_user.first_name

    text = f"""Приветствуем, {username} ⚡

1xBet KG — удобный сервис для пополнения и вывода средств без комиссии в Кыргызстане 🇰🇬

🪙 0% комиссия на пополнение и вывод

🔒 Безопасные и защищённые транзакции

⚡ Обработка заявок: от 1 до 5 секунд

💬 Наш чат: @betkg

Служба поддержки: @betkg
"""

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda m: m.text == "👤 Баланс")
def balance(message):
    bal = balances.get(message.from_user.id, 0)
    bot.send_message(message.chat.id, f"Сиздин баланс: {bal} сом")
    bot.send_message(
        message.chat.id,
        "Башкы меню",
        reply_markup=main_menu()
    )

bot.infinity_polling()

@bot.message_handler(func=lambda m: m.text == "💳 Пополнение")
def deposit(message):
    bot.send_message(message.chat.id, "Пополнение суммасын жазыңыз. Мисалы: 500")
    bot.register_next_step_handler(message, deposit_amount)

def deposit_amount(message):
    try:
        amount = int(message.text)
        if amount <= 0:
            raise ValueError
        amounts[message.from_user.id] = amount
        bot.send_message(message.chat.id, "Эми төлөмдүн чек/скриншотун жибериңиз 📸")
    except:
        bot.send_message(message.chat.id, "Сумманы туура жазыңыз. Мисалы: 500")

@bot.message_handler(content_types=["photo"])
def check_photo(message):
    uid = message.from_user.id

    if uid not in amounts:
        bot.send_message(message.chat.id, "Алгач 💳 Пополнение басып, сумманы жазыңыз.")
        return

    amount = amounts[uid]

    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("✅ Бекитүү", callback_data=f"approve_{uid}_{amount}"))

    username = message.from_user.username or "username жок"

    caption = (
        "💳 Жаңы пополнение заявка\n\n"
        f"👤 User ID: {uid}\n"
        f"🔗 Username: @{username}\n"
        f"💰 Сумма: {amount} сом"
    )

    bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=caption, reply_markup=kb)
    bot.send_message(message.chat.id, "Заявка админге жөнөтүлдү. Текшерүүнү күтүңүз ⏳")

@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_"))
def approve(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "Сиз админ эмессиз.")
        return

    _, uid, amount = call.data.split("_")
    uid = int(uid)
    amount = int(amount)

    balances[uid] = balances.get(uid, 0) + amount

    bot.send_message(uid, f"✅ Пополнение бекитилди. Балансыңызга {amount} сом кошулду.")
    bot.answer_callback_query(call.id, "Бекитилди ✅")

@bot.message_handler(func=lambda m: m.text == "💸 Вывод")
def withdraw(message):
    bot.send_message(message.chat.id, "Вывод суммасын жана реквизитти жазыңыз.\nМисалы: 300 сом, MBank +996...")
    bot.register_next_step_handler(message, withdraw_info)

def withdraw_info(message):
    uid = message.from_user.id
    username = message.from_user.username or "username жок"

    bot.send_message(
        ADMIN_ID,
        f"💸 Вывод заявка\n\n👤 User ID: {uid}\n🔗 Username: @{username}\n📄 Маалымат: {message.text}"
    )
    bot.send_message(message.chat.id, "Вывод заявка админге жөнөтүлдү ✅")

@bot.message_handler(func=lambda m: m.text == "📞 Поддержка")
def support(message):
    bot.send_message(message.chat.id, "Поддержка: @сенин_username")

print("Бот иштеп жатат...")
bot.infinity_polling()

