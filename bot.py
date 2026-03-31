import os
from flask import Flask, request
import telebot

# Get token and chat ID from Render Environment Variables
TOKEN = os.environ.get("BOT_TOKEN")
YOUR_CHAT_ID = int(os.environ.get("YOUR_CHAT_ID"))

# Safety check
if not TOKEN or not YOUR_CHAT_ID:
    raise ValueError("BOT_TOKEN and YOUR_CHAT_ID must be set in Render Environment Variables!")

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

message_mapping = {}

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "OK", 200

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Hello!\n\n"
                          "Send any message, question or confession.\n"
                          "It will be sent to the owner anonymously.")

@bot.message_handler(func=lambda m: True)
def handle_all(message):
    user_id = message.chat.id

    # If message is from you (owner) - replying to user
    if user_id == YOUR_CHAT_ID:
        if message.reply_to_message and message.reply_to_message.message_id in message_mapping:
            original_user = message_mapping[message.reply_to_message.message_id]
            try:
                bot.copy_message(original_user, YOUR_CHAT_ID, message.message_id)
                bot.send_message(YOUR_CHAT_ID, "✅ Reply sent anonymously!")
            except:
                bot.send_message(YOUR_CHAT_ID, "❌ Failed to send reply.")
        else:
            bot.send_message(YOUR_CHAT_ID, "Please reply directly to a forwarded message.")
        return

    # Message from normal user
    try:
        sent = bot.copy_message(YOUR_CHAT_ID, user_id, message.message_id)
        message_mapping[sent.message_id] = user_id
        bot.reply_to(message, "✅ Your message has been sent anonymously!")
    except:
        bot.reply_to(message, "❌ Error occurred.")

@app.route("/")
def home():
    return "Anonymous Bot is running on Render!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
