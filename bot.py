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
    asset_mode="lazy",
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


def get_number(value):
    if value is None:
        return None

    try:
        value = float(value)

        if value <= 0:
            return None

        return value

    except:
        return None


def get_market_prices(prices):

    if not isinstance(prices, dict):
        return {}

    result = {}

    fragment_keys = [
        "fragment_price_ton",
        "fragment_floor_price_ton",
        "fragment_floor",
    ]

    getgems_keys = [
        "getgems_price_ton",
        "getgems_floor_price_ton",
        "getgems_floor",
    ]

    tgmrkt_keys = [
        "tgmrkt_price_ton",
        "tgmrkt_floor_price_ton",
        "tgmrkt_floor",
    ]

    for key in fragment_keys:
        value = get_number(prices.get(key))

        if value is not None:
            result["Fragment"] = value
            break

    for key in getgems_keys:
        value = get_number(prices.get(key))

        if value is not None:
            result["GetGems"] = value
            break

    for key in tgmrkt_keys:
        value = get_number(prices.get(key))

        if value is not None:
            result["TGMrkt"] = value
            break

    return result


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🎁 FloorRadarXBot\n\n"
        "NFT link yuboring.\n"
        "Men collection floor narxlarini tekshiraman.\n\n"
        "/gifts — barcha giftlar\n"
        "/search NOM — gift qidirish"
    )


async def check_nft(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.strip()

    match = re.search(
        r"https?://t\.me/nft/([A-Za-z0-9_]+)-(\d+)",
        text,
        re.IGNORECASE,
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

    await update.message.reply_text(
        "⏳ Floor narxlar tekshirilmoqda..."
    )

    try:

        print(
            f"QIDIRILMOQDA: {collection} #{nft_id}",
            flush=True,
        )

        info = gifts.get_gift(collection)

        if not info:

            await update.message.reply_text(
                f"❌ Gift topilmadi.\n\n"
                f"Collection: {collection}"
            )

            return

        prices = info.get("prices", {})

        print(
            f"{collection} PRICES: {repr(prices)}",
            flush=True,
        )

        market_prices = get_market_prices(prices)

        gift_name = (
            info.get("full_name")
            or info.get("name")
            or collection
        )

        message = (
            f"🎁 {gift_name}\n"
            f"🆔 NFT ID: #{nft_id}\n\n"
            f"💎 FLOOR PRICES\n"
        )

        if not market_prices:

            message += (
                "❌ Hozircha real floor narx "
                "ma'lumoti topilmadi.\n\n"
                f"🔎 Collection: {collection}"
            )

            await update.message.reply_text(message)

            return

        values = []

        for market, value in market_prices.items():

            message += (
                f"🔹 {market}: "
                f"{value:g} TON\n"
            )

            values.append(value)

        lowest = min(values)

        message += (
            f"\n📉 Eng past floor: "
            f"{lowest:g} TON"
        )

        await update.message.reply_text(message)

    except Exception as e:

        print(
            f"NFT XATO: {repr(e)}",
            flush=True,
        )

        await update.message.reply_text(
            "⚠️ NFT ma'lumotlarini olishda xatolik."
        )


async def all_gifts(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "⏳ Barcha giftlar yuklanmoqda..."
    )

    try:

        regular_gifts = gifts.get_regular_gifts()

        print(
            f"GIFTLAR SONI: {len(regular_gifts)}",
            flush=True,
        )

        if not regular_gifts:

            await update.message.reply_text(
                "❌ Giftlar topilmadi."
            )

            return

        chunk = ""
        part = 1

        for i, gift in enumerate(
            regular_gifts,
            1,
        ):

            name = (
                getattr(
                    gift,
                    "full_name",
                    None,
                )
                or getattr(
                    gift,
                    "name",
                    "Noma'lum",
                )
            )

            floor = get_number(
                getattr(
                    gift,
                    "floor_price",
                    None,
                )
            )

            if floor is not None:

                floor_text = (
                    f"{floor:g} TON"
                )

            else:

                floor_text = (
                    "Narx topilmadi"
                )

            line = (
                f"{i}. 🎁 {name}\n"
                f"💎 Floor: {floor_text}\n\n"
            )

            if len(chunk) + len(line) > 3500:

                await update.message.reply_text(
                    f"🎁 GIFTLAR — {part}-qism\n\n"
                    f"{chunk}"
                )

                part += 1
                chunk = ""

            chunk += line

        if chunk:

            await update.message.reply_text(
                f"🎁 GIFTLAR — {part}-qism\n\n"
                f"{chunk}"
            )

    except Exception as e:

        print(
            f"GIFTLAR XATO: {repr(e)}",
            flush=True,
        )

        await update.message.reply_text(
            "⚠️ Giftlar ro'yxatini olishda xatolik."
        )


async def search_gift(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not context.args:

        await update.message.reply_text(
            "❌ Gift nomini yozing.\n\n"
            "Misol:\n"
            "/search HomemadeCake"
        )

        return

    query = " ".join(
        context.args
    ).lower()

    await update.message.reply_text(
        f"🔎 Qidirilmoqda: {query}"
    )

    try:

        regular_gifts = (
            gifts.get_regular_gifts()
        )

        found = []

        for gift in regular_gifts:

            name = (
                getattr(
                    gift,
                    "full_name",
                    None,
                )
                or getattr(
                    gift,
                    "name",
                    "",
                )
            )

            if query in name.lower():

                found.append(gift)

        if not found:

            await update.message.reply_text(
                "❌ Gift topilmadi."
            )

            return

        message = (
            f"🎁 TOPILDI: "
            f"{len(found)} ta\n\n"
        )

        for gift in found[:20]:

            name = (
                getattr(
                    gift,
                    "full_name",
                    None,
                )
                or getattr(
                    gift,
                    "name",
                    "Noma'lum",
                )
            )

            floor = get_number(
                getattr(
                    gift,
                    "floor_price",
                    None,
                )
            )

            if floor is not None:

                floor_text = (
                    f"{floor:g} TON"
                )

            else:

                floor_text = (
                    "Narx topilmadi"
                )

            message += (
                f"🎁 {name}\n"
                f"💎 Floor: {floor_text}\n\n"
            )

        await update.message.reply_text(
            message
        )

    except Exception as e:

        print(
            f"SEARCH XATO: {repr(e)}",
            flush=True,
        )

        await update.message.reply_text(
            "⚠️ Qidirishda xatolik."
        )


def main():

    if not TOKEN:

        raise RuntimeError(
            "TOKEN environment variable topilmadi!"
        )

    print(
        "TOKEN TOPILDI",
        flush=True,
    )

    threading.Thread(
        target=run_server,
        daemon=True,
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
            start,
        )
    )

    app.add_handler(
        CommandHandler(
            "gifts",
            all_gifts,
        )
    )

    app.add_handler(
        CommandHandler(
            "search",
            search_gift,
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT
            & ~filters.COMMAND,
            check_nft,
        )
    )

    print(
        "FloorRadarXBot ishga tushdi!",
        flush=True,
    )

    app.run_polling()


if __name__ == "__main__":
    main()
