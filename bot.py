import os
import logging
import threading
from flask import Flask, request
from dotenv import load_dotenv
import telebot
import sheets_logger

# Load environment variables from .env file in the script's folder
script_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(script_dir, ".env"))

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

if not TOKEN:
    print("❌ ERROR: TELEGRAM_BOT_TOKEN is not set.")
    print("\nSetup:")
    print("  1. Copy .env.example to .env")
    print("  2. Set TELEGRAM_BOT_TOKEN=your_token_here")
    import sys
    sys.exit(1)

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    return 'Forbidden', 403


# Set webhook if WEBHOOK_URL or RENDER_EXTERNAL_URL is configured
public_url = os.getenv("WEBHOOK_URL") or os.getenv("RENDER_EXTERNAL_URL")
if public_url:
    logger.info(f"Setting webhook to {public_url}/webhook...")
    bot.remove_webhook()
    bot.set_webhook(url=f"{public_url}/webhook")


def _log(user, action: str, detail: str = ""):
    """Log a char counter event to Google Sheets (non-blocking)."""
    threading.Thread(
        target=sheets_logger.log_char_counter,
        args=(user, action, detail),
        daemon=True
    ).start()


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "🤖 *Welcome to Character Counter Bot!*\n\n"
        "I can help you quickly count characters, words, and lines in any text.\n\n"
        "👉 *How to use:*\n"
        "1. *Forward* a message from any chat or channel to me.\n"
        "2. Or simply type or paste any text directly.\n\n"
        "I will instantly reply with a detailed count breakdown!\n\n"
        "🔗 _Open source — [github.com/futurecoderin/char-counter-bot](https://github.com/futurecoderin/char-counter-bot)_"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown", disable_web_page_preview=True)
    _log(message.from_user, "/start or /help")


@bot.message_handler(
    func=lambda message: True,
    content_types=['text', 'photo', 'video', 'document', 'audio', 'voice']
)
def analyze_message(message):
    # Extract text from message or media caption
    text = message.text or message.caption

    if not text:
        bot.reply_to(
            message,
            "⚠️ *No text found!*\n\nPlease forward or send a message that contains text or a caption.",
            parse_mode="Markdown"
        )
        _log(message.from_user, "No Text Sent", "Media without caption")
        return

    # Calculate metrics
    char_count_total    = len(text)
    char_count_no_spaces = len(text.replace(" ", "").replace("\n", "").replace("\r", "").replace("\t", ""))
    word_count          = len(text.split())
    line_count          = len(text.splitlines())

    is_forwarded = getattr(message, 'forward_date', None) is not None
    header = "📨 *Forwarded Message Analysis*" if is_forwarded else "📊 *Text Analysis*"

    response = (
        f"{header}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"• *Total Characters:* `{char_count_total}` (including spaces)\n"
        f"• *Characters (no spaces):* `{char_count_no_spaces}`\n"
        f"• *Words:* `{word_count}`\n"
        f"• *Lines:* `{line_count}`\n"
    )

    if not is_forwarded:
        response += "\n💡 _Tip: You can also forward messages from other chats!_"

    bot.reply_to(message, response, parse_mode="Markdown")

    action = "Forwarded Message" if is_forwarded else "Text Analyzed"
    detail = f"chars={char_count_total}, words={word_count}, lines={line_count}"
    _log(message.from_user, action, detail)


if __name__ == "__main__":
    if public_url:
        port = int(os.getenv("PORT", 8080))
        app.run(host="0.0.0.0", port=port)
    else:
        logger.info("Starting Character Counter Bot in polling mode...")
        print("Bot is running... Press Ctrl+C to stop.")
        try:
            bot.remove_webhook()
            try:
                bot.set_my_description(
                    "📊 Count characters, words, and lines in any text instantly!\n\n"
                    "Just send or forward any message and get a detailed breakdown.\n\n"
                    "Open source: github.com/futurecoderin/char-counter-bot"
                )
                bot.set_my_short_description(
                    "Count characters, words & lines in any text instantly."
                )
                logger.info("Bot description updated.")
            except Exception as e:
                logger.warning(f"Could not set bot description: {e}")
            bot.infinity_polling()
        except Exception as e:
            logger.error(f"Error: {e}")
