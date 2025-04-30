import requests
import telegram
import asyncio
from datetime import datetime
import pytz
import os
import logging

# تنظیمات لاگ‌ها
logging.basicConfig(level=logging.INFO)

# تنظیمات
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # توکن از GitHub Secrets
CHANNEL_ID = "@LiveRatecrypto"  # آیدی کانال
NOBITEX_API = "https://api.nobitex.ir/v2/trades/USDTIRT"
BINANCE_BTC_API = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
BINANCE_ETH_API = "https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT"

# تنظیم منطقه زمانی ایران
IRAN_TZ = pytz.timezone("Asia/Tehran")

async def get_nobitex_price():
    try:
        response = requests.get(NOBITEX_API, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data.get("status") == "ok" and data.get("trades"):
            last_trade = data["trades"][0]["price"]
            return int(last_trade) / 10  # تبدیل به تومان
        logging.warning(f"Nobitex API warning: Unexpected response -> {data}")
        return None
    except Exception as e:
        logging.error(f"Error fetching Nobitex price: {str(e)}")
        return None

async def get_binance_price(api_url):
    try:
        response = requests.get(api_url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if "price" in data:
            return float(data["price"])
        logging.warning(f"Binance API warning: Unexpected response -> {data}")
        return None
    except Exception as e:
        logging.error(f"Error fetching Binance price: {str(e)}")
        return None

async def send_to_telegram(bot):
