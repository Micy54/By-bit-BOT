import os
import time
import requests
from pybit.unified_trading import HTTP
from keep_alive import keep_alive
import numpy as np
import telepot

# === CONFIG ===
API_KEY = os.getenv("BYBIT_API_KEY")
API_SECRET = os.getenv("BYBIT_API_SECRET")
SYMBOL = "DOGEUSDT"
INTERVAL = 1  # in minuti
QTY_USDT = 3
LEVERAGE = 5
TG_CHAT_ID = 464125829
TG_TOKEN = "7704558648:AAEF-9T8wzy650t1QetQ6TfcbhK6gxuxpQU"

session = HTTP(api_key=API_KEY, api_secret=API_SECRET)

# === FUNZIONI BASE ===
def get_klines():
    r = session.get_kline(category="linear", symbol=SYMBOL, interval=str(INTERVAL), limit=20)
    return [float(k["close"]) for k in r["result"]["list"]][-1:]

def send_telegram(msg):
    try:
        bot = telepot.Bot(TG_TOKEN)
        bot.sendMessage(TG_CHAT_ID, msg)
    except Exception as e:
        print(f"[ERRORE Telegram] {e}")

# === STRATEGIA ===
def rsi(data):
    gain = [data[i] - data[i - 1] for i in range(1, len(data)) if data[i] > data[i - 1]]
    loss = [data[i - 1] - data[i] for i in range(1, len(data)) if data[i] < data[i - 1]]

    avg_gain = np.mean(gain) if gain else 0
    avg_loss = np.mean(loss) if loss else 0

    rs = avg_gain / avg_loss if avg_loss != 0 else 0
    rsi_value = 100 - (100 / (1 + rs))
    return rsi_value

def bollinger(data):
    ma = np.mean(data)
    std_dev = np.std(data)
    upper = ma + 2 * std_dev
    lower = ma - 2 * std_dev
    return ma, upper, lower

def place_order(order_type):
    if order_type == "Buy":
        print(f"[ORDER] Buy signal triggered")
        # Inserisci qui il codice per inviare un ordine long
    elif order_type == "Sell":
        print(f"[ORDER] Sell signal triggered")
        # Inserisci qui il codice per inviare un ordine short

# === CICLO PRINCIPALE ===
def main_loop():
    keep_alive()
    while True:
        try:
            data = get_klines()
            rsi_value = rsi(data)
            ma, upper, lower = bollinger(data)
            last_price = data[-1]

            print(f"[MONITOR] RSI: {rsi_value:.2f} | Price: {last_price:.4f}")
            send_telegram(f"[MONITOR] RSI: {rsi_value:.2f} | Price: {last_price:.4f}")

            # TEST: RSI trigger più facile
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
    send_telegram("🤖 Bot avviato e operativo.")
    print("🔥 Ciclo partito")
    send_telegram("🔥 Ciclo monitoraggio partito correttamente.")
    main_loop()
