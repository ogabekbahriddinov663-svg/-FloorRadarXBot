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


# Render Web Service uchun
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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom 👋\n\n"
        "Telegram NFT linkini yuboring.\n\n"
        "Men giftning floor narxlarini tekshiraman.\n\n"
        "Misol:\n"
        "https://t.me/nft/HexPot-56196"
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
            "https://t.me/nft/HexPot-56196"
        )
        return

    collection = match.group(1)
    nft_id = match.group(2)

    await update.message.reply_text(
        f"🔎 NFT tekshirilmoqda...\n\n"
        f"📦 Collection: {collection}\n"
        f"🔢 ID: #{nft_id}"
    )

    try:
        # Butun gift katalogini olish
        all_gifts = gifts.get_regular_gifts()

        found = None

        # Katalogdan collectionni qidirish
        for gift in all_gifts:

            full_name = str(
                getattr(gift, "full_name", "") or ""
            )

            name = str(
                getattr(gift, "name", "") or ""
            )

            if (
                collection.lower() == full_name.lower()
                or collection.lower() == name.lower()
                or collection.lower() in full_name.lower()
                or collection.lower() in name.lower()
            ):
                found = gift
                break

        if not found:
            await update.message.reply_text(
                "❌ Bu gift katalogdan topilmadi.\n\n"
                f"🔎 Qidirilgan: {collection}\n\n"
                "Collection nomini tekshirib qayta urinib ko‘ring."
            )
            return

        # Gift nomi
        gift_name = getattr(
            found,
            "full_name",
            collection
        )

        # Floor price
        floor_price = getattr(
            found,
            "floor_price",
            None
        )

        message = (
            f"🎁 {gift_name}\n\n"
            f"🆔 NFT ID: #{nft_id}\n"
        )

        if floor_price is not None:
            message += (
                f"\n💎 Floor: {floor_price} TON\n"
            )

        # Marketplace narxlarini olish
        try:
            info = gifts.get_gift(
                str(gift_name)
            )

            if info:
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

                message += "\n📊 Marketplace:\n"

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

        except Exception as price_error:
            print(
                "Marketplace error:",
                repr(price_error)
            )

        await update.message.reply_text(
            message
        )

    except Exception as e:

        print(
            "XATO:",
            repr(e)
        )

        await update.message.reply_text(
            "⚠️ Gift ma’lumotlarini olishda "
            "xatolik yuz berdi.\n\n"
            "Birozdan keyin qayta urinib ko‘ring."
        )


def main():

    if not TOKEN:
        raise RuntimeError(
            "TOKEN environment variable topilmadi!"
        )

    # Render uchun port
    threading.Thread(
        target=run_server,
        daemon=True
    ).start()

    app = Application.builder().token(
        TOKEN
    ).build()

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

    print("Bot ishga tushdi!")

    app.run_polling()


if __name__ == "__main__":
    main()
