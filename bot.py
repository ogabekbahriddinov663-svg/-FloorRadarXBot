
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


# =========================
# RENDER WEB SERVER
# =========================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header(
            "Content-type",
            "text/plain"
        )
        self.end_headers()

        self.wfile.write(
            b"FloorRadarXBot is running!"
        )

    def log_message(self, format, *args):
        pass


def run_server():

    server = HTTPServer(
        ("0.0.0.0", PORT),
        HealthHandler
    )

    print(
        f"Web server {PORT} portda ishlayapti"
    )

    server.serve_forever()


# =========================
# START
# =========================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "Salom 👋\n\n"
        "Telegram NFT linkini yuboring.\n\n"
        "Men giftning floor narxini "
        "tekshiraman.\n\n"
        "Misol:\n"
        "https://t.me/nft/HexPot-56196"
    )


# =========================
# NFT CHECK
# =========================

async def check_nft(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    text = update.message.text.strip()

    match = re.search(
        r"https?://t\.me/nft/"
        r"([A-Za-z0-9_]+)-(\d+)",
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

        # =========================
        # BUTUN GIFT KATALOGI
        # =========================

        all_gifts = gifts.get_regular_gifts()


        print(
            "GIFTLAR SONI:",
            len(all_gifts)
        )


        found = None


        # =========================
        # COLLECTION QIDIRISH
        # =========================

        for gift in all_gifts:

            full_name = str(
                getattr(
                    gift,
                    "full_name",
                    ""
                ) or ""
            )

            name = str(
                getattr(
                    gift,
                    "name",
                    ""
                ) or ""
            )


            collection_lower = (
                collection.lower()
            )


            if (
                collection_lower
                == full_name.lower()
                or
                collection_lower
                == name.lower()
                or
                collection_lower
                in full_name.lower()
                or
                collection_lower
                in name.lower()
            ):

                found = gift
                break


        # =========================
        # TOPILMADI
        # =========================

        if not found:

            await update.message.reply_text(
                "❌ Bu gift katalogdan "
                "topilmadi.\n\n"
                f"🔎 Qidirilgan: {collection}\n\n"
                "Collection nomini tekshirib "
                "qayta urinib ko‘ring."
            )

            return


        # =========================
        # GIFT NOMI
        # =========================

        gift_name = getattr(
            found,
            "full_name",
            collection
        )


        # =========================
        # FLOOR
        # =========================

        floor_price = getattr(
            found,
            "floor_price",
            None
        )


        message = (
            f"🎁 {gift_name}\n\n"
            f"🆔 NFT ID: #{nft_id}\n\n"
        )


        if floor_price is not None:

            message += (
                f"💎 Floor: "
                f"{floor_price} TON\n"
            )


        # =========================
        # MARKETPLACE
        # =========================

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


                message += (
                    "\n📊 Marketplace:\n"
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


        except Exception as e:

            print(
                "Marketplace error:",
                repr(e)
            )


        # =========================
        # JAVOB
        # =========================

        await update.message.reply_text(
            message
        )


    except Exception as e:

        print(
            "XATO:",
            repr(e)
        )


        await update.message.reply_text(
            "⚠️ Gift ma’lumotlarini "
            "olishda xatolik yuz berdi.\n\n"
            "Birozdan keyin qayta urinib "
            "ko‘ring."
        )


# =========================
# MAIN
# =========================

def main():

    if not TOKEN:

        raise RuntimeError(
            "TOKEN environment variable "
            "topilmadi!"
        )


    # Render server

    threading.Thread(
        target=run_server,
        daemon=True
    ).start()


    # Telegram bot

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
            filters.TEXT
            & ~filters.COMMAND,
            check_nft
        )
    )


    print(
        "FloorRadarXBot ishga tushdi!"
    )


    app.run_polling()


if __name__ == "__main__":
    main()
