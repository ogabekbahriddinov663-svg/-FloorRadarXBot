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
    server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
    print(f"WEB SERVER: {PORT}", flush=True)
    server.serve_forever()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom 👋\n\n"
        "🎁 Telegram Gift bot\n\n"
        "/gifts — barcha giftlar\n"
        "/search NOM — gift qidirish\n\n"
        "NFT link yuborsangiz, uning ma'lumotlarini ham tekshiraman."
    )


async def all_gifts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⏳ Barcha giftlar yuklanmoqda..."
    )

    try:
        regular_gifts = gifts.get_regular_gifts()

        print(
            f"GIFTLAR SONI: {len(regular_gifts)}",
            flush=True
        )

        if not regular_gifts:
            await update.message.reply_text(
                "❌ Gift katalogi bo'sh."
            )
            return

        # Telegram xabarining uzunligi cheklangan.
        # Giftlarni bo'lib yuboramiz.
        lines = []

        for i, gift in enumerate(regular_gifts, 1):
            name = getattr(gift, "full_name", None) or getattr(
                gift, "name", "Noma'lum"
            )

            floor = getattr(gift, "floor_price", None)

            if floor is not None:
                price = f"{floor} TON"
            else:
                price = "Narx yo'q"

            lines.append(
                f"{i}. 🎁 {name}\n"
                f"   💎 Floor: {price}"
            )

        # 3500 belgidan oshirmay bo'lib yuborish
        chunk = ""
        part = 1

        for line in lines:
            if len(chunk) + len(line) + 2 > 3500:
                await update.message.reply_text(
                    f"🎁 GIFTLAR — {part}-qism\n\n{chunk}"
                )
                part += 1
                chunk = ""

            chunk += line + "\n\n"

        if chunk:
            await update.message.reply_text(
                f"🎁 GIFTLAR — {part}-qism\n\n{chunk}"
            )

    except Exception as e:
        print(
            f"GIFTLAR XATO: {repr(e)}",
            flush=True
        )

        await update.message.reply_text(
            "⚠️ Giftlar ro'yxatini olishda xatolik yuz berdi."
        )


async def search_gift(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "❌ Gift nomini yozing.\n\n"
            "Misol:\n"
            "/search HomemadeCake"
        )
        return

    query = " ".join(context.args).lower()

    await update.message.reply_text(
        f"🔎 Qidirilmoqda: {query}"
    )

    try:
        regular_gifts = gifts.get_regular_gifts()

        found = []

        for gift in regular_gifts:
            name = (
                getattr(gift, "full_name", None)
                or getattr(gift, "name", "")
            )

            if query in name.lower():
                found.append(gift)

        if not found:
            await update.message.reply_text(
                f"❌ Gift topilmadi.\n\n"
                f"🔎 Qidirilgan: {query}"
            )
            return

        message = f"🎁 TOPILDI: {len(found)} ta\n\n"

        for gift in found[:20]:
            name = (
                getattr(gift, "full_name", None)
                or getattr(gift, "name", "Noma'lum")
            )

            floor = getattr(gift, "floor_price", None)

            if floor is not None:
                price = f"{floor} TON"
            else:
                price = "Narx yo'q"

            message += (
                f"🎁 {name}\n"
                f"💎 Floor: {price}\n\n"
            )

        await update.message.reply_text(message)

    except Exception as e:
        print(
            f"SEARCH XATO: {repr(e)}",
            flush=True
        )

        await update.message.reply_text(
            "⚠️ Qidirishda xatolik yuz berdi."
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
            "❌ NFT link noto'g'ri.\n\n"
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
                f"🔎 Qidirilgan: {collection}\n\n"
                f"💡 /search {collection}"
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
            "⚠️ Gift ma'lumotlarini olishda xatolik yuz berdi."
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
        CommandHandler("gifts", all_gifts)
    )

    bot.add_handler(
        CommandHandler("search", search_gift)
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
