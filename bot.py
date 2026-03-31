import os
from flask import Flask, request
import telebot

TOKEN = os.environ.get("8777170699:AAEt8qddcDCeW3qCn4JpEKmfi6k7oOJg9LA")          # We'll add this on Render
YOUR_CHAT_ID = int(os.environ.get("5356823467"))   # We'll add this too

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# Store mapping for replies
message_mapping = {}

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "OK", 200

# Welcome message
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Hello!\n\nSend any message, question, or confession.\nIt will be forwarded anonymously.\n\nYou can also send photos, voice, etc.")

# Main handler
@bot.message_handler(func=lambda m: True)
def handle_all(message):
    user_id = message.chat.id

    # Reply from you (owner)
    if user_id == YOUR_CHAT_ID:
        if message.reply_to_message and message.reply_to_message.message_id in message_mapping:
            original_user = message_mapping[message.reply_to_message.message_id]
            try:
                bot.copy_message(original_user, YOUR_CHAT_ID, message.message_id)
                bot.send_message(YOUR_CHAT_ID, "✅ Reply sent anonymously!")
            except:
                bot.send_message(YOUR_CHAT_ID, "❌ Failed to send reply.")
        else:
            bot.send_message(YOUR_CHAT_ID, "Reply to a forwarded message to answer.")
        return

    # Message from normal user
    try:
        sent = bot.copy_message(YOUR_CHAT_ID, user_id, message.message_id)
        message_mapping[sent.message_id] = user_id
        bot.reply_to(message, "✅ Your message has been sent anonymously!")
    except:
        bot.reply_to(message, "❌ Error occurred.")

# Set webhook when the app starts
@app.route("/")
def set_webhook():
    bot.remove_webhook()
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
    bot.set_webhook(url=webhook_url)
    return f"Webhook set to: {webhook_url}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)