import os
import time
import requests
from pybit.unified_trading import HTTP
from keep_alive import keep_alive
import numpy as np
import telegram

# === CONFIG ===
API_KEY = os.getenv("BYBIT_API_KEY")
API_SECRET = os.getenv("BYBIT_API_SECRET")
SYMBOL = "DOGEUSDT"
INTERVAL = 1  # in minuti
QTY_USDT = 3
LEVERAGE = 5
TG_CHAT_ID = 464125829
TG_TOKEN = "7704558648:AAEf-9I8wzy650t1Qet06TfcbhK6gxuxpQU"

session = HTTP(api_key=API_KEY, api_secret=API_SECRET)

# === FUNZIONI BASE ===
def get_klines():
    r = session.get_kline(category="linear", symbol=SYMBOL, interval=str(INTERVAL), limit=20)
    return [float(k["close"]) for k in r["result"]["list"]][::-1]

def rsi(prices, period=14):
    prices = np.array(prices)
    delta = np.diff(prices)
    gain = np.mean(delta[delta > 0]) if np.any(delta > 0) else 0
    loss = -np.mean(delta[delta < 0]) if np.any(delta < 0) else 0
    rs = gain / loss if loss != 0 else 100
    return 100 - (100 / (1 + rs))

def bollinger(prices, period=20):
    prices = np.array(prices[-period:])
    ma = np.mean(prices)
    std = np.std(prices)
    return ma, ma + 2 * std, ma - 2 * std

def place_order(side):
    try:
        price = float(session.get_orderbook(symbol=SYMBOL)["result"]["b"][0][0])
        order = session.place_order(
            category="linear",
            symbol=SYMBOL,
            side=side,
            order_type="Market",
            qty=round(QTY_USDT * LEVERAGE / price, 2),
            time_in_force="GoodTillCancel",
            reduce_only=False
        )
        print(f"[ORDER] {side} → {order['retMsg']}")
        send_telegram(f"✅ Ordine {side} eseguito: {order['retMsg']}")
    except Exception as e:
        print("[ERRORE]", e)
        send_telegram(f"[ERRORE] {e}")

def send_telegram(msg):
    try:
        bot = telegram.Bot(token=TG_TOKEN)
        bot.send_message(chat_id=TG_CHAT_ID, text=msg)
    except Exception as e:
        print("[TELEGRAM ERROR]", e)

# === CICLO PRINCIPALE ===
def main_loop():
    keep_alive()
    send_telegram("🤖 Bot avviato e operativo.")
    while True:
        try:
            data = get_klines()
            rsi_value = rsi(data)
            ma, upper, lower = bollinger(data)
            last_price = data[-1]

            print(f"[MONITOR] RSI: {rsi_value:.2f} | Price: {last_price:.4f}")
            send_telegram(f"[MONITOR] RSI: {rsi_value:.2f} | Price: {last_price:.4f}")

            if rsi_value < 25 and last_price < lower:
                place_order("Buy")
            elif rsi_value > 75 and last_price > upper:
                place_order("Sell")

        except Exception as e:
            print("[ERRORE]", e)
            send_telegram(f"[ERRORE] {e}")

        time.sleep(60)

# === AVVIO ===
if __name__ == "__main__":
    main_loop()
