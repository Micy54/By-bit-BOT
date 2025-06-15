import os
import time
import requests
from pybit.unified_trading import HTTP
import telepot

# API Keys
API_KEY = os.getenv("BYBIT_API_KEY")
API_SECRET = os.getenv("BYBIT_API_SECRET")
TG_TOKEN = os.getenv("TG_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")

# Inizializza Bybit sessione
session = HTTP(api_key=API_KEY, api_secret=API_SECRET)

# Inizializza Telegram bot
bot = telepot.Bot(TG_TOKEN)

def send_telegram(msg):
    try:
        bot.sendMessage(TG_CHAT_ID, msg)
    except Exception as e:
        print(f"[ERROR] Telegram not sent: {e}")

def get_klines():
    try:
        r = session.get_kline(category="linear", symbol="DOGEUSDT", interval="1", limit=20)
        return [float(k["close"]) for k in r["result"]["list"]]
    except Exception as e:
        print(f"[ERROR] Failed to fetch kline data: {e}")
        return []

def rsi(data, period=14):
    gains = []
    losses = []
    for i in range(1, period + 1):
        delta = data[i] - data[i - 1]
        if delta > 0:
            gains.append(delta)
        else:
            losses.append(abs(delta))
    avg_gain = sum(gains) / period if gains else 0
    avg_loss = sum(losses) / period if losses else 0
    rs = avg_gain / avg_loss if avg_loss else 0
    return 100 - (100 / (1 + rs))

def main():
    send_telegram("Bot started and monitoring.")
    while True:
        data = get_klines()
        if len(data) < 14:
            print("[ERROR] Not enough data to calculate RSI")
            time.sleep(60)
            continue

        rsi_value = rsi(data)
        print(f"[INFO] RSI: {rsi_value}")
        if rsi_value < 30:
            send_telegram("RSI below 30: Buying opportunity")
            # Implement Buy logic
        elif rsi_value > 70:
            send_telegram("RSI above 70: Selling opportunity")
            # Implement Sell logic

        time.sleep(60)  # Delay for 1 minute

if __name__ == "__main__":
    main()
