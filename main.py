import os
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot ishlayapti!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! 👋 Gift nomini yuboring.")

async def text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gift = update.message.text
    await update.message.reply_text(
        f"🎁 {gift}\n\nFloor narx tekshirilmoqda..."
    )

def main():
    Thread(target=run_web).start()

    bot = Application.builder().token(TOKEN).build()
    bot.add_handler(CommandHandler("start", start))
    bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text))

    print("Bot ishga tushdi!")
    bot.run_polling()

if __name__ == "__main__":
    main()
