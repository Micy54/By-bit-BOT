import os, time
import numpy as np
from pybit.unified_trading import HTTP
import telepot

# Config
API_KEY     = os.getenv("BYBIT_API_KEY")
API_SECRET  = os.getenv("BYBIT_API_SECRET")
TG_TOKEN    = os.getenv("TG_TOKEN")
TG_CHAT_ID  = os.getenv("TG_CHAT_ID")
SYMBOL      = "DOGEUSDT"
INTERVAL    = "1"  # minuti

# Setup sessioni
session = HTTP(api_key=API_KEY, api_secret=API_SECRET)
bot     = telepot.Bot(TG_TOKEN)

def send_msg(text):
    try:
        bot.sendMessage(TG_CHAT_ID, text)
    except Exception as e:
        print(f"[TELEGRAM] {e}")

def get_prices(limit=20):
    data = session.get_kline(category="linear", symbol=SYMBOL,
                             interval=INTERVAL, limit=limit)
    closes = [float(k["close"]) for k in data["result"]["list"]]
    return np.array(closes)

def ema(arr, period):
    return arr.ewm(span=period, adjust=False).mean() if ... else None

def main():
    send_msg("Bot partito su DOGE!")
    while True:
        try:
            prices = get_prices()
            # TODO: calcola ema_fast, ema_slow, condizioni di entrata/uscita
            # TODO: esegui order via: session.place_active_order(...)
            # TODO: notifica e log
            time.sleep(60)
        except Exception as e:
            print(f"[ERROR] {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()
