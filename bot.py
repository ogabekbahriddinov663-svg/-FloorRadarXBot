import os
import re
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from TelegramGifts import TelegramGifts


print("BOT.PY BOSHLANDI", flush=True)

TOKEN = os.getenv("TOKEN")
PORT = int(os.getenv("PORT", "10000"))

gifts = TelegramGifts(
    cache_mode="http",
    asset_mode="lazy"
)


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"FloorRadarXBot is running!")

    def log_message(self, format, *args):
        pass


def run_server():
    server = HTTPServer(
        ("0.0.0.0", PORT),
        HealthHandler
    )
    print(f"WEB SERVER: {PORT}", flush=True)
    server.serve_forever()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom 👋\n\n"
        "Telegram NFT linkini yuboring.\n\n"
        "Misol:\n"
        "https://t.me/nft/HomemadeCake-1453"
    )


async def check_nft(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    match = re.search(
        r"https?://t\.me/nft/([A-Za-z0-9_]+)-(\d+)",
        text,
        re.IGNORECASE
    )

    if not match:
        await update.message.reply_text(
            "❌ NFT link noto‘g‘ri.\n\n"
            "Misol:\n"
            "https://t.me/nft/HomemadeCake-1453"
        )
        return

    collection = match.group(1)
    nft_id = match.group(2)

    await update.message.reply_text(
        f"🔎 Tekshirilmoqda...\n\n"
        f"🎁 Collection: {collection}\n"
        f"🆔 NFT ID: #{nft_id}"
    )

    try:
        print(
            f"QIDIRILMOQDA: {collection}",
            flush=True
        )

        info = gifts.get_gift(collection)

        if not info:
            await update.message.reply_text(
                f"❌ Gift topilmadi.\n\n"
                f"🔎 Qidirilgan: {collection}"
            )
            return

        prices = info.get("prices", {})

        fragment = prices.get("fragment_price_ton")
        getgems = prices.get("getgems_price_ton")
        tgmrkt = prices.get("tgmrkt_price_ton")

        gift_name = info.get(
            "full_name",
            collection
        )

        message = (
            f"🎁 {gift_name}\n"
            f"🆔 NFT ID: #{nft_id}\n\n"
            f"💎 Floor narxlar:\n"
        )

        if fragment is not None:
            message += f"🔹 Fragment: {fragment} TON\n"

        if getgems is not None:
            message += f"🔹 GetGems: {getgems} TON\n"

        if tgmrkt is not None:
            message += f"🔹 TGMrkt: {tgmrkt} TON\n"

        if (
            fragment is None
            and getgems is None
            and tgmrkt is None
        ):
            message += "❌ Narx topilmadi.\n"

        await update.message.reply_text(message)

    except Exception as e:
        print(
            f"NFT XATO: {repr(e)}",
            flush=True
        )

        await update.message.reply_text(
            "⚠️ Gift ma’lumotlarini olishda "
            "xatolik yuz berdi."
        )


def main():
    if not TOKEN:
        raise RuntimeError(
            "TOKEN environment variable topilmadi!"
        )

    print("TOKEN TOPILDI", flush=True)

    threading.Thread(
        target=run_server,
        daemon=True
    ).start()

    bot = Application.builder().token(TOKEN).build()

    bot.add_handler(
        CommandHandler("start", start)
    )

    bot.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            check_nft
        )
    )

    print(
        "FloorRadarXBot ishga tushdi!",
        flush=True
    )

    bot.run_polling()


if __name__ == "__main__":
    main()
