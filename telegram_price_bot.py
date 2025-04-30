import requests
import telegram
import asyncio
import json
from datetime import datetime
import pytz
import os

# تنظیمات
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # توکن از GitHub Secrets
CHANNEL_ID = "@LiveRatecrypto"  # آیدی کانال
NOBITEX_API = "https://api.nobitex.ir/v2/trades/USDTIRT"
BYBIT_API = "https://api.bybit.com/v5/market/tickers?category=spot"

# تنظیم منطقه زمانی ایران
IRAN_TZ = pytz.timezone("Asia/Tehran")

async def get_nobitex_price():
    try:
        response = requests.get(NOBITEX_API, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data["status"] == "ok":
            last_trade = data["trades"][0]["price"]
            return int(last_trade) / 10  # تبدیل به تومان
        print(f"Nobitex API error: status not ok, data: {data}")
        return None
    except Exception as e:
        print(f"Error fetching Nobitex price: {str(e)}")
        return None

async def get_bybit_prices():
    try:
        response = requests.get(BYBIT_API, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data["retCode"] == 0:
            btc_price = None
            eth_price = None
            for item in data["result"]["list"]:
                if item["symbol"] == "BTCUSDT":
                    btc_price = float(item["lastPrice"]) if item["lastPrice"] else None
                elif item["symbol"] == "ETHUSDT":
                    eth_price = float(item["lastPrice"]) if item["lastPrice"] else None
            if not btc_price or not eth_price:
                print(f"Bybit API error: incomplete data, response: {data}")
            return btc_price, eth_price
        print(f"Bybit API error: retCode not 0, data: {data}")
        return None, None
    except Exception as e:
        print(f"Error fetching Bybit prices: {str(e)}")
        return None, None

async def send_to_telegram():
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    
    # دریافت قیمت‌ها
    tether_price = await get_nobitex_price()
    btc_price, eth_price = await get_bybit_prices()
    
    # زمان فعلی ایران
    now = datetime.now(IRAN_TZ).strftime("%Y-%m-%d %H:%M:%S")
    
    # ساخت پیام
    message = ""
    message += f"💵 USDIRT: {tether_price:,.2f} IRT\n" if tether_price else "💵 USDIRT: ⚠️ خطا\n"
    message += f"₿ BTCUSDT: ${btc_price:,.2f}\n" if btc_price else "₿ BTCUSDT: ⚠️ خطا\n"
    message += f"Ξ ETHUSDT: ${eth_price:,.2f}\n" if eth_price else "Ξ ETHUSDT: ⚠️ خطا\n"
    message += f"{now}"
    
    # ارسال پیام به کانال
    try:
        await bot.send_message(chat_id=CHANNEL_ID, text=message)
        print(f"Message sent at {now}")
    except Exception as e:
        print(f"Error sending message: {str(e)}")

async def main():
    while True:
        await send_to_telegram()
        await asyncio.sleep(60)  # اجرا هر 1 دقیقه

if __name__ == "__main__":
    asyncio.run(main())
