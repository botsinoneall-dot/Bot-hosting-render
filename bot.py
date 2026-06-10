import os
import telebot
import requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
ADMIN_ID = int(os.environ['TELEGRAM_ADMIN_ID'])
RENDER_API_KEY = os.environ['RENDER_API_KEY']
RENDER_SERVICE_ID = os.environ['RENDER_SERVICE_ID']

bot = telebot.TeleBot(API_TOKEN)

RENDER_HEADERS = {
    "Authorization": f"Bearer {RENDER_API_KEY}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Unauthorized access. This is a private hosting panel.")
        return

    banner_url = "https://images.unsplash.com/photo-1614064641938-3bbee52942c7?w=800"

    caption_text = (
        "🦋 👋 HELLO ⛓️‍💥✖️SAYKO_KILLER☯️ ࿐~✖️💨\n\n"
        "⚡ **PYTHON BOT HOSTING**\n\n"
        "🧠 **HOST YOUR BOT WITH:**\n"
        "🩸 NO DOCKER & VPS\n"
        "⚙️ FAST RENDER DEPLOY\n"
        "🔥 ONLY FOR LIGHTWEIGHT BOTS\n\n"
        "➡️ **USE BUTTONS BELOW**"
    )

    markup = InlineKeyboardMarkup(row_width=2)
    btn_coder = InlineKeyboardButton("✨ DEPLOY BOT NOW ✨", callback_data="deploy_bot")
    btn_panel = InlineKeyboardButton("🌐 CHECK HOSTING STATUS 🌐", callback_data="check_status")
    btn_dev = InlineKeyboardButton("👤 DEVELOPER", callback_data="developer")
    btn_help = InlineKeyboardButton("❓ HELP", callback_data="help")
    btn_about = InlineKeyboardButton("ℹ️ ABOUT", callback_data="about")

    markup.add(btn_coder)
    markup.add(btn_panel)
    markup.add(btn_dev, btn_help)
    markup.add(btn_about)

    bot.send_photo(message.chat.id, photo=banner_url, caption=caption_text, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "Unauthorized!", show_alert=True)
        return

    if call.data == "deploy_bot":
        bot.answer_callback_query(call.id, "Sending Deploy Command...", show_alert=False)
        url = f"https://api.render.com/v1/services/{RENDER_SERVICE_ID}/deploys"
        try:
            response = requests.post(url, headers=RENDER_HEADERS, json={})
            if response.status_code in [200, 201]:
                bot.send_message(call.message.chat.id, "🚀 **Success!** Render deployment started.", parse_mode="Markdown")
            else:
                bot.send_message(call.message.chat.id, f"❌ **Failed.** Code: {response.status_code}", parse_mode="Markdown")
        except Exception as e:
            bot.send_message(call.message.chat.id, f"⚠️ Error: {str(e)}")

    elif call.data == "check_status":
        bot.answer_callback_query(call.id, "Fetching system status...", show_alert=False)
        url = f"https://api.render.com/v1/services/{RENDER_SERVICE_ID}"
        try:
            response = requests.get(url, headers=RENDER_HEADERS)
            if response.status_code == 200:
                data = response.json()
                service_status = data.get("status", "unknown").upper()
                status_msg = f"🖥️ **Render Host Status:**\n\n🔹 **Status:** {service_status}\n🔹 **Service Name:** `{data.get('name')}`"
                bot.send_message(call.message.chat.id, status_msg, parse_mode="Markdown")
            else:
                bot.send_message(call.message.chat.id, "❌ Could not fetch status.")
        except Exception as e:
            bot.send_message(call.message.chat.id, f"⚠️ Error: {str(e)}")

    elif call.data == "developer":
        bot.send_message(call.message.chat.id, "👤 Panel Owner: @SAYKO_KILLER")
    elif call.data == "help":
        bot.send_message(call.message.chat.id, "❓ Send /start to reload.")
    elif call.data == "about":
        bot.send_message(call.message.chat.id, "ℹ️ Render Private Control Panel v1.0")

print("Hosting panel bot is starting...")
bot.infinity_polling()
