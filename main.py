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
import os
import time
import numpy as np
import pandas as pd
from pybit.unified_trading import HTTP
import telepot

# CONFIG
API_KEY     = os.getenv("BYBIT_API_KEY")
API_SECRET  = os.getenv("BYBIT_API_SECRET")
TG_TOKEN    = os.getenv("TG_TOKEN")
TG_CHAT_ID  = os.getenv("TG_CHAT_ID")
SYMBOL      = "DOGEUSDT"
INTERVAL    = "1"  # minuti
QUANTITY    = 100  # Modifica in base al tuo capitale

# SESSIONS
session = HTTP(api_key=API_KEY, api_secret=API_SECRET)
bot = telepot.Bot(TG_TOKEN)

# UTILS
def send_msg(text):
    try:
        bot.sendMessage(TG_CHAT_ID, text)
    except Exception as e:
        print(f"[TELEGRAM ERROR] {e}")

def get_prices(limit=50):
    data = session.get_kline(category="linear", symbol=SYMBOL,
                             interval=INTERVAL, limit=limit)
    closes = [float(k["close"]) for k in data["result"]["list"]]
    return closes[::-1]  # reverse per ordine cronologico

def get_ema(data, period):
    df = pd.Series(data)
    return df.ewm(span=period, adjust=False).mean().iloc[-1]

def get_position():
    pos = session.get_positions(category="linear", symbol=SYMBOL)
    size = float(pos["result"]["list"][0]["size"])
    side = pos["result"]["list"][0]["side"]
    return size, side

def close_position():
    size, side = get_position()
    if size > 0:
        opposite = "Sell" if side == "Buy" else "Buy"
        session.place_order(category="linear", symbol=SYMBOL,
                            side=opposite, order_type="Market",
                            qty=size, reduce_only=True)
        send_msg(f"❌ Posizione chiusa: {side}, size {size}")

def open_position(side):
    session.place_order(category="linear", symbol=SYMBOL,
                        side=side, order_type="Market",
                        qty=QUANTITY, reduce_only=False)
    send_msg(f"✅ Nuova posizione: {side}, size {QUANTITY}")

# MAIN LOOP
def main():
    send_msg("🤖 Bot DOGE partito (EMA strategy)!")
    while True:
        try:
            closes = get_prices()
            ema9 = get_ema(closes, 9)
            ema21 = get_ema(closes, 21)

            size, side = get_position()

            if ema9 > ema21 and (size == 0 or side == "Sell"):
                close_position()
                open_position("Buy")

            elif ema9 < ema21 and (size == 0 or side == "Buy"):
                close_position()
                open_position("Sell")

            print(f"EMA9: {ema9:.5f} | EMA21: {ema21:.5f}")
            time.sleep(60)

        except Exception as e:
            send_msg(f"[ERROR] {e}")
            print(f"[ERROR] {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()
