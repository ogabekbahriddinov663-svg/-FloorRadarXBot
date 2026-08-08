# bot.py
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
PORT = int(os.getenv("PORT", "10000"))

gifts = TelegramGifts(
    cache_mode="http",
    asset_mode="lazy",
    ttl_seconds=300
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
    server.serve_forever()


def price(prices, names):
    if not isinstance(prices, dict):
        return None

    for name in names:
        value = prices.get(name)
        if value not in (None, 0, 0.0, "0", "0.0"):
            return value

    return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎁 FloorRadarXBot\n\n"
        "NFT link yuboring — floor price tekshiriladi.\n\n"
        "/gifts — barcha giftlar\n"
        "/search NOM — gift qidirish"
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
            "https://t.me/nft/HomemadeCake-173766"
        )
        return

    collection = match.group(1)
    nft_id = match.group(2)

    await update.message.reply_text("⏳ Floor narx tekshirilmoqda...")

    try:
        info = gifts.get_gift(collection)

        if not info:
            await update.message.reply_text(
                f"❌ {collection} topilmadi."
            )
            return

        prices = info.get("prices", {})

        print(
            f"{collection} PRICES: {repr(prices)}",
            flush=True
        )

        fragment = price(
            prices,
            [
                "fragment_price_ton",
                "fragment_floor_price_ton",
                "fragment_floor"
            ]
        )

        getgems = price(
            prices,
            [
                "getgems_price_ton",
                "getgems_floor_price_ton",
                "getgems_floor"
            ]
        )

        tgmrkt = price(
            prices,
            [
                "tgmrkt_price_ton",
                "tgmrkt_floor_price_ton",
                "tgmrkt_floor"
            ]
        )

        gift_name = (
            info.get("full_name")
            or info.get("name")
            or collection
        )

        result = (
            f"🎁 {gift_name}\n"
            f"🆔 NFT ID: #{nft_id}\n\n"
            f"💎 FLOOR PRICE:\n"
        )

        values = []

        if fragment is not None:
            result += f"🔹 Fragment: {fragment} TON\n"
            values.append(float(fragment))

        if getgems is not None:
            result += f"🔹 GetGems: {getgems} TON\n"
            values.append(float(getgems))

        if tgmrkt is not None:
            result += f"🔹 TGMrkt: {tgmrkt} TON\n"
            values.append(float(tgmrkt))

        if values:
            result += (
                f"\n📉 Eng past floor: "
                f"{min(values):g} TON"
            )
        else:
            result += "\n❌ Real floor price topilmadi."

        await update.message.reply_text(result)

    except Exception as e:
        print(f"NFT XATO: {repr(e)}", flush=True)

        await update.message.reply_text(
            "⚠️ Floor price olishda xatolik."
        )


async def all_gifts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Giftlar yuklanmoqda...")

    try:
        regular_gifts = gifts.get_regular_gifts()

        lines = []

        for i, gift in enumerate(regular_gifts, 1):
            name = (
                getattr(gift, "full_name", None)
                or getattr(gift, "name", "Noma'lum")
            )

            floor = getattr(gift, "floor_price", None)

            if floor not in (None, 0, 0.0):
                text = f"{floor} TON"
            else:
                text = "Narx topilmadi"

            lines.append(
                f"{i}. 🎁 {name}\n"
                f"💎 Floor: {text}"
            )

        chunk = ""
        part = 1

        for line in lines:
            if len(chunk) + len(line) > 3500:
                await update.message.reply_text(
                    f"🎁 GIFTLAR {part}-qism\n\n{chunk}"
                )
                part += 1
                chunk = ""

            chunk += line + "\n\n"

        if chunk:
            await update.message.reply_text(
                f"🎁 GIFTLAR {part}-qism\n\n{chunk}"
            )

    except Exception as e:
        print(f"GIFTLAR XATO: {repr(e)}", flush=True)

        await update.message.reply_text(
            "⚠️ Giftlar yuklanmadi."
        )


async def search_gift(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "❌ Misol: /search HomemadeCake"
        )
        return

    query = " ".join(context.args).lower()

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
                "❌ Gift topilmadi."
            )
            return

        result = f"🎁 TOPILDI: {len(found)} ta\n\n"

        for gift in found[:20]:
            name = (
                getattr(gift, "full_name", None)
                or getattr(gift, "name", "Noma'lum")
            )

            floor = getattr(gift, "floor_price", None)

            if floor not in (None, 0, 0.0):
                floor_text = f"{floor} TON"
            else:
                floor_text = "Narx topilmadi"

            result += (
                f"🎁 {name}\n"
                f"💎 Floor: {floor_text}\n\n"
            )

        await update.message.reply_text(result)

    except Exception as e:
        print(f"SEARCH XATO: {repr(e)}", flush=True)

        await update.message.reply_text(
            "⚠️ Qidirishda xatolik."
        )


def main():
    if not TOKEN:
        raise RuntimeError("TOKEN topilmadi!")

    threading.Thread(
        target=run_server,
        daemon=True
    ).start()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gifts", all_gifts))
    app.add_handler(CommandHandler("search", search_gift))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            check_nft
        )
    )

    print("FloorRadarXBot ishga tushdi!", flush=True)

    app.run_polling()


if __name__ == "__main__":
    main()
