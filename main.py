import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! 👋\n"
        "NFT nomini yuboring, tekshiramiz."
    )

async def text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nft = update.message.text
    await update.message.reply_text(
        f"🔎 {nft}\n\n"
        "Floor narx tekshirilmoqda..."
    )

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, text))

    print("FloorRadarXBot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()
