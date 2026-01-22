import telebot
from telebot import types
import config

bot = telebot.TeleBot(config.TOKEN)

user_states = {}
messages_storage = {}

# /start
@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("📝 Надіслати новину")

    bot.send_message(
        message.chat.id,
        "Привіт шановний, цей бот створений для питань та повідомлень про цілі по Запоріжжю",
        reply_markup=keyboard
    )

# Кнопка "Надіслати новину"
@bot.message_handler(func=lambda m: m.text == "📝 Надіслати новину")
def send_news(message):
    user_states[message.chat.id] = "waiting_text"
    bot.send_message(message.chat.id, "Напишіть що хочете надіслати")

# Отримання тексту від користувача
@bot.message_handler(func=lambda m: user_states.get(m.chat.id) == "waiting_text")
def get_text(message):
    user_states.pop(message.chat.id)

    text = message.text
    user_id = message.chat.id

    messages_storage[user_id] = text

    admin_keyboard = types.InlineKeyboardMarkup()
    admin_keyboard.add(
        types.InlineKeyboardButton("✉️ Відповісти", callback_data=f"reply_{user_id}"),
        types.InlineKeyboardButton("❌ Видалити", callback_data=f"delete_{user_id}")
    )

    bot.send_message(
        config.ADMIN_ID,
        f"📩 Нове повідомлення:\n\n{text}\n\n👤 ID: {user_id}",
        reply_markup=admin_keyboard
    )

    bot.send_message(user_id, "Очікуйте відповідь від адміністратора")

# Callback від адміна
@bot.callback_query_handler(func=lambda call: True)
def admin_actions(call):
    if call.data.startswith("reply_"):
        user_id = int(call.data.split("_")[1])
        user_states[config.ADMIN_ID] = f"replying_{user_id}"
        bot.send_message(config.ADMIN_ID, "Напишіть відповідь користувачу")

    elif call.data.startswith("delete_"):
        user_id = int(call.data.split("_")[1])
        messages_storage.pop(user_id, None)
        bot.edit_message_text(
            "❌ Повідомлення видалено",
            call.message.chat.id,
            call.message.message_id
        )

# Відповідь адміна користувачу
@bot.message_handler(func=lambda m: str(user_states.get(m.chat.id, "")).startswith("replying_"))
def send_reply(message):
    user_id = int(user_states[message.chat.id].split("_")[1])
    user_states.pop(message.chat.id)

    bot.send_message(user_id, f"📨 Відповідь адміністратора:\n\n{message.text}")
    bot.send_message(message.chat.id, "✅ Відповідь надіслана")

# Запуск
bot.infinity_polling()
