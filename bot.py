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


TOKEN = os.getenv("TOKEN")
PORT = int(os.getenv("PORT", 10000))

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

    print(f"Web server {PORT} portda ishlayapti")
    server.serve_forever()


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "Salom 👋\n\n"
        "Telegram NFT linkini yuboring.\n\n"
        "Men NFT giftning floor narxini "
        "tekshiraman.\n\n"
        "Misol:\n"
        "https://t.me/nft/HomemadeCake-1453"
    )


async def check_nft(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

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
        # Giftni to‘g‘ridan-to‘g‘ri nomi orqali qidiramiz
        info = gifts.get_gift(collection)

        if not info:
            # Ba'zi nomlar boshqa formatda bo‘lishi mumkin
            info = gifts.get_gift(
                collection.replace("_", " ")
            )

        if not info:
            await update.message.reply_text(
                "❌ Gift topilmadi.\n\n"
                f"🎁 Collection: {collection}\n\n"
                "Linkni tekshirib qayta urinib ko‘ring."
            )
            return

        full_name = info.get(
            "full_name",
            collection
        )

        prices = info.get(
            "prices",
            {}
        )

        fragment = prices.get(
            "fragment_price_ton"
        )

        getgems = prices.get(
            "getgems_price_ton"
        )

        tgmrkt = prices.get(
            "tgmrkt_price_ton"
        )

        message = (
            f"🎁 {full_name}\n"
            f"🆔 NFT ID: #{nft_id}\n\n"
            f"💎 FLOOR PRICES\n\n"
        )

        if fragment is not None:
            message += (
                f"🔹 Fragment: "
                f"{fragment} TON\n"
            )

        if getgems is not None:
            message += (
                f"🔹 GetGems: "
                f"{getgems} TON\n"
            )

        if tgmrkt is not None:
            message += (
                f"🔹 TGMrkt: "
                f"{tgmrkt} TON\n"
            )

        if (
            fragment is None
            and getgems is None
            and tgmrkt is None
        ):
            message += (
                "❌ Hozircha narx "
                "ma'lumotlari mavjud emas.\n"
            )

        await update.message.reply_text(
            message
        )

    except Exception as e:

        print(
            "NFT ERROR:",
            repr(e)
        )

        await update.message.reply_text(
            "⚠️ NFT ma’lumotlarini olishda "
            "xatolik yuz berdi.\n\n"
            "Birozdan keyin qayta urinib ko‘ring."
        )


def main():

    if not TOKEN:
        raise RuntimeError(
            "TOKEN environment variable topilmadi!"
        )

    threading.Thread(
        target=run_server,
        daemon=True
    ).start()

    app = (
        Application
        .builder()
        .token(TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            check_nft
        )
    )

    print(
        "FloorRadarXBot ishga tushdi!"
    )

    app.run_polling()


if __name__ == "__main__":

    main(
