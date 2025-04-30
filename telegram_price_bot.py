import requests
import telegram
import asyncio
from datetime import datetime
import pytz
import os

# تنظیمات
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # توکن از GitHub Secrets
CHANNEL_ID = "@LiveRatecrypto"  # آیدی کانال
NOBITEX_API = "https://api.nobitex.ir/v2/trades/USDTIRT"
BINANCE_BTC_API = "https://api.nobitex.ir/v2/trades/BTCUSDT"
BINANCE_ETH_API = "https://api.nobitex.ir/v2/trades/ETHUSDT"

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

async def get_binance_price(api_url, symbol):
    try:
        response = requests.get(api_url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if "price" in data and data["symbol"] == symbol:
            return float(data["price"])
        print(f"Binance API error for {symbol}: invalid data, response: {data}")
        return None
    except Exception as e:
        print(f"Error fetching Binance price for {symbol}: {str(e)}")
        return None

async def send_to_telegram():
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    
    # دریافت قیمت‌ها
    tether_price = await get_nobitex_price()
    btc_price = await get_binance_price(BINANCE_BTC_API, "BTCUSDT")
    eth_price = await get_binance_price(BINANCE_ETH_API, "ETHUSDT")
    
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
        await asyncio.sleep(120)  # اجرا هر 2 دقیقه

if __name__ == "__main__":
    asyncio.run(main())
