import os
import logging
from flask import Flask, request
from dotenv import load_dotenv
import telebot

# Load environment variables (check both .env and env.txt in the script's folder)
script_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(script_dir, ".env"))
if not os.getenv("TELEGRAM_BOT_TOKEN"):
    load_dotenv(os.path.join(script_dir, "env.txt"))

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

if not TOKEN:
    print("❌ ERROR: TELEGRAM_BOT_TOKEN is not set in the env.txt or .env file!")
    print("\nHow to configure:")
    print("1. Search for @BotFather on Telegram and start a chat.")
    print("2. Send '/newbot' and follow instructions to get your Token.")
    print("3. Paste the token into the 'env.txt' file inside 'telegram_bot/':")
    print("   TELEGRAM_BOT_TOKEN=your_actual_token_here")
    import sys
    sys.exit(0)

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    else:
        return 'Forbidden', 403

# Automatically set webhook if RENDER_EXTERNAL_URL is available
public_url = os.getenv("RENDER_EXTERNAL_URL")
if public_url:
    logger.info(f"Setting webhook to {public_url}/webhook...")
    bot.remove_webhook()
    bot.set_webhook(url=f"{public_url}/webhook")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "🤖 **Welcome to Character Counter Bot!**\n\n"
        "I can help you quickly count characters, words, and lines in your text.\n\n"
        "👉 **How to use:**\n"
        "1. **Forward** a message from any chat or channel to me.\n"
        "2. Or simply send/type a message directly to me.\n\n"
        "I will immediately reply with a detailed count analysis!"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'video', 'document', 'audio', 'voice'])
def analyze_message(message):
    # Check if there is text content (either in message text or media caption)
    text = message.text or message.caption
    
    if not text:
        # User sent a media file without any text/caption
        bot.reply_to(
            message,
            "⚠️ **No text found!**\n\nPlease forward or send a message that contains text or a caption.",
            parse_mode="Markdown"
        )
        return

    # Calculate metrics
    char_count_total = len(text)
    char_count_no_spaces = len(text.replace(" ", "").replace("\n", "").replace("\r", "\t").replace("\t", ""))
    word_count = len(text.split())
    line_count = len(text.splitlines()) if text else 0

    # Determine if the message was forwarded
    is_forwarded = getattr(message, 'forward_date', None) is not None

    header = "📨 **Forwarded Message Analysis**" if is_forwarded else "📊 **Text Analysis**"
    
    response = (
        f"{header}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"• **Total Characters:** `{char_count_total}` (including spaces)\n"
        f"• **Characters (no spaces):** `{char_count_no_spaces}`\n"
        f"• **Words:** `{word_count}`\n"
        f"• **Lines:** `{line_count}`\n"
    )

    if not is_forwarded:
        response += "\n💡 *Tip: You can also forward messages from other chats to me!*"

    bot.reply_to(message, response, parse_mode="Markdown")

if __name__ == "__main__":
    if public_url:
        # Run Flask development server when executing locally with RENDER_EXTERNAL_URL
        port = int(os.getenv("PORT", 8080))
        app.run(host="0.0.0.0", port=port)
    else:
        logger.info("Starting char_counterBot polling locally...")
        print("Bot is running in polling mode... Press Ctrl+C to stop.")
        try:
            bot.remove_webhook()
            bot.infinity_polling()
        except Exception as e:
            logger.error(f"Error occurred: {e}")
