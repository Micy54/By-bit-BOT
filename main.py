import os
import time
import requests
from pybit.unified_trading import HTTP
from keep_alive import keep_alive

API_KEY = os.getenv("BYBIT_API_KEY")
API_SECRET = os.getenv("BYBIT_API_SECRET")
SYMBOL = "FARTCOINUSDT"
INTERVAL = 1
QTY_USDT = 3
LEVERAGE = 5

session = HTTP(api_key=API_KEY, api_secret=API_SECRET)

def get_klines():
    r = session.get_kline(
        category="linear",
        symbol=SYMBOL,
        interval=str(INTERVAL),
        limit=20
    )
    return [float(k["close"]) for k in r["result"]["list"]][::-1]

def rsi(data, period=14):
    gains, losses = [], []
    for i in range(1, period + 1):
        delta = data[i] - data[i - 1]
        (gains if delta > 0 else losses).append(abs(delta))
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    rs = avg_gain / avg_loss if avg_loss != 0 else 0
    return 100 - (100 / (1 + rs))

def bollinger(data, period=20):
    ma = sum(data[-period:]) / period
    std_dev = (sum((x - ma) ** 2 for x in data[-period:]) / period) ** 0.5
    return ma, ma + 2 * std_dev, ma - 2 * std_dev

def place_order(side):
    price = float(session.get_ticker(symbol=SYMBOL)["result"]["list"][0]["lastPrice"])
    qty = round(QTY_USDT / price * LEVERAGE, 4)
    session.place_order(
        category="linear",
        symbol=SYMBOL,
        side=side,
        order_type="Market",
        qty=qty,
        reduce_only=False,
        time_in_force="GoodTillCancel"
    )
    print(f"{side} order placed at {price}")

def main_loop():
    keep_alive()
    while True:
        try:
            data = get_klines()
            rsi_value = rsi(data)
            ma, upper, lower = bollinger(data)

            last_price = data[-1]
            print(f"RSI: {rsi_value:.2f} | Price: {last_price:.4f}")

            if rsi_value < 25 and last_price < lower:
                place_order("Buy")
            elif rsi_value > 75 and last_price > upper:
                place_order("Sell")

        except Exception as e:
            print("Errore:", e)

        time.sleep(60)

if __name__ == "__main__":
    main_loop()
