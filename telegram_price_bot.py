import requests
import telegram
import asyncio
from datetime import datetime
import pytz
import os

# تنظیمات
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # توکن از GitHub Secrets
CHANNEL_ID = "@LiveRatecrypto"  # آیدی کانال
NOBITEX_API_TETHER = "https://api.nobitex.ir/v2/trades/USDTIRT"
LBank_API_BTC = "https://api.lbkex.com/v2/ticker.do?symbol=BTC_USDT"
LBank_API_ETH = "https://api.lbkex.com/v2/ticker.do?symbol=ETH_USDT"
IRAN_TZ = pytz.timezone("Asia/Tehran")


# دریافت قیمت تتر از نوبیتکس
async def get_nobitex_price():
    try:
        response = requests.get(NOBITEX_API_TETHER, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data["status"] == "ok":
            last_trade = data["trades"][0]["price"]
            return int(last_trade) / 10  # تبدیل به تومان
        return None
    except Exception as e:
        print(f"Error fetching Nobitex price: {e}")
        return None


# دریافت قیمت از LBank برای BTC و ETH
async def get_lbank_price(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if "ticker" in data:
            last_price = data["ticker"]["last"]
            return float(last_price)  # قیمت آخر
        return None
    except Exception as e:
        print(f"Error fetching LBank price: {e}")
        return None


async def send_to_telegram(bot):
    tether_price = await get_nobitex_price()  # قیمت تتر از نوبیتکس
    btc_price = await get_lbank_price(LBank_API_BTC)  # قیمت بیت‌کوین از LBank
    eth_price = await get_lbank_price(LBank_API_ETH)  # قیمت اتریوم از LBank
    now = datetime.now(IRAN_TZ).strftime("%Y-%m-%d %H:%M:%S")

    message = ""
    message += f"💵 USDIRT: {tether_price:,.2f} IRT\n" if tether_price else "💵 USDIRT: ⚠️ خطا\n"
    message += f"₿ BTCUSDT: ${btc_price:,.2f}\n" if btc_price else "₿ BTCUSDT: ⚠️ خطا\n"
    message += f"Ξ ETHUSDT: ${eth_price:,.2f}\n" if eth_price else "Ξ ETHUSDT: ⚠️ خطا\n"
    message += f"{now}"

    try:
        await bot.send_message(chat_id=CHANNEL_ID, text=message)
        print(f"✅ Message sent at {now}")
    except Exception as e:
        print(f"Error sending message: {e}")


async def main():
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    while True:
        await send_to_telegram(bot)
        await asyncio.sleep(60)  # اجرا هر 1 دقیقه


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Unhandled error: {e}")
