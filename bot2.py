import os
import telebot
from telebot import types
import random
import string
import time

# Read bot token from environment variable
BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# Optional: Gmail credentials (for future use)
GMAIL_EMAIL = os.environ.get("GMAIL_EMAIL")
GMAIL_PASSWORD = os.environ.get("GMAIL_PASSWORD")

# Temporary storage (replace with database for production)
users = {}

def generate_email():
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    return f"{username}@gmail.com", password

# Start command
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    if chat_id not in users:
        users[chat_id] = {"balance": 0, "hold": 0, "tasks_completed": 0, "referrals": 0}
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📝 Task", "💼 Balance")
    markup.row("💰 Withdraw", "🔗 Referral Link")
    bot.send_message(chat_id, "Welcome! Select an option:", reply_markup=markup)

# Task command
@bot.message_handler(func=lambda message: message.text == "📝 Task")
def task(message):
    chat_id = message.chat.id
    email, password = generate_email()
    users[chat_id]["current_task"] = {"email": email, "password": password, "reward": 40}

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Done Task", callback_data="done_task"))
    markup.add(types.InlineKeyboardButton("❌ Cancel Task", callback_data="cancel_task"))

    task_text = f"""
Task: Task 1 (fast check) - 40 PKR
Random Generated Email: {email}
Password: {password}

👉 Click Here: /rules
Please complete the registration and press one of the buttons below
"""
    bot.send_message(chat_id, task_text, reply_markup=markup)

# Callback handling for task buttons
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if call.data == "done_task":
        if "current_task" in users[chat_id]:
            users[chat_id]["hold"] += users[chat_id]["current_task"]["reward"]
            bot.answer_callback_query(call.id, "Task submitted! Waiting for approval (30 mins).")
            bot.send_message(chat_id, f"💰 Hold: {users[chat_id]['hold']} PKR")
            # Simulate 30 min approval for demo (replace with scheduler in production)
            time.sleep(1)
            users[chat_id]["balance"] += users[chat_id]["current_task"]["reward"]
            users[chat_id]["tasks_completed"] += 1
            del users[chat_id]["current_task"]
    elif call.data == "cancel_task":
        bot.answer_callback_query(call.id, "Task cancelled.")
        del users[chat_id]["current_task"]

# Balance command
@bot.message_handler(func=lambda message: message.text == "💼 Balance")
def balance(message):
    chat_id = message.chat.id
    user = users[chat_id]
    bot.send_message(chat_id, f"""
💼 Account Summary
📊 Balance: {user['balance']} PKR
✅ Tasks Completed: {user['tasks_completed']}
🔒 Hold: {user['hold']} PKR
""")

# Withdraw command
@bot.message_handler(func=lambda message: message.text == "💰 Withdraw")
def withdraw(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("Easypaisa", "JazzCash")
    markup.row("Bank", "Binance")
    bot.send_message(message.chat.id, "Please select your withdrawal method:", reply_markup=markup)

# Referral Link
@bot.message_handler(func=lambda message: message.text == "🔗 Referral Link")
def referral(message):
    link = f"https://t.me/YourBotUsername?start={message.chat.id}"
    bot.send_message(message.chat.id, f"Your referral link:\n{link}")

# Rules command
@bot.message_handler(commands=['rules'])
def rules(message):
    rules_text = """
🌟 (Rules) 🌟
1️⃣ Use the given Username + Password to create Gmail.
2️⃣ After creating Gmail, delete it from your mobile.
3️⃣ Press Done Task only after completing Gmail.
4️⃣ Changing password or selling Gmail elsewhere will ban your ID.
💎 Work with honesty.
"""
    bot.send_message(message.chat.id, rules_text)

# Run the bot
bot.polling()
