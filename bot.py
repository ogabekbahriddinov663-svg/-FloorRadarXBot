import os
import re

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom 👋\n\n"
        "Telegram NFT linkini yuboring.\n\n"
        "Misol:\n"
        "https://t.me/nft/HexPot-56196"
    )


async def check_nft(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    match = re.search(
        r"https://t\.me/nft/([A-Za-z0-9]+)-(\d+)",
        text
    )

    if match:
        collection = match.group(1)
        nft_id = match.group(2)

        await update.message.reply_text(
            "✅ NFT topildi\n\n"
            f"📦 Collection: {collection}\n"
            f"🔢 ID: #{nft_id}\n\n"
            "⏳ Floor price funksiyasi keyin qo‘shiladi..."
        )
    else:
        await update.message.reply_text(
            "❌ NFT link noto‘g‘ri.\n\n"
            "Misol:\n"
            "https://t.me/nft/HexPot-56196"
        )


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, check_nft)
    )

    print("Bot ishga tushdi!")
    app.run_polling()


if __name__ == "__main__":
    main()
