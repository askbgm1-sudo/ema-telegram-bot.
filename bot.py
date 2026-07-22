from binance.client import Client
import pandas as pd
import requests
import time

# ==============================
# TELEGRAM
# ==============================
BOT_TOKEN = "8881743343:AAHcpQeiseM4BVapefSCj4UBSJ9hrDScGNs"
CHAT_ID = "698764150"

client = Client()

COINS = [
    "JTOUSDT",
    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "DOGEUSDT",
    "ADAUSDT",
    "TRXUSDT",
    "LINKUSDT",
    "AVAXUSDT"
]

INTERVAL = Client.KLINE_INTERVAL_1HOUR

last_signal = {}
last_candle = {}

# ==============================
# TELEGRAM MESSAGE
# ==============================
def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": message
        }
    )

# ==============================
# BINANCE DATA
# ==============================
def get_data(symbol):
    klines = client.get_klines(
        symbol=symbol,
        interval=INTERVAL,
        limit=100
    )

    df = pd.DataFrame(klines, columns=[
        "Open Time","Open","High","Low","Close","Volume",
        "Close Time","Quote Asset Volume","Trades",
        "TB Base","TB Quote","Ignore"
    ])

    df["Close"] = df["Close"].astype(float)

    df["EMA9"] = df["Close"].ewm(span=9, adjust=False).mean()
    df["EMA21"] = df["Close"].ewm(span=21, adjust=False).mean()

    return df

# ==============================
# CHECK SIGNAL
# ==============================
def check_signal(symbol):
    global last_signal
    global last_candle

    df = get_data(symbol)

    candle = df.iloc[-1]["Close Time"]

    if last_candle.get(symbol) == candle:
        return

    last_candle[symbol] = candle

    prev = df.iloc[-2]
    curr = df.iloc[-1]

    signal = None

    if prev["EMA9"] < prev["EMA21"] and curr["EMA9"] > curr["EMA21"]:
        signal = "BUY"

    elif prev["EMA9"] > prev["EMA21"] and curr["EMA9"] < curr["EMA21"]:
        signal = "SELL"

    if signal:

        if last_signal.get(symbol) == signal:
            return

        last_signal[symbol] = signal

        message = (
            f"🚨 {signal} SIGNAL\n\n"
            f"🪙 Coin : {symbol}\n"
            f"⏰ Timeframe : 1H\n"
            f"💰 Price : {curr['Close']}"
        )

        send_telegram(message)
        print(message)

# ==============================
# MAIN LOOP
# ==============================
print("🚀 EMA Bot Started...")

while True:

    for coin in COINS:
        try:
            check_signal(coin)
        except Exception as e:
            print(f"{coin} : {e}")

    time.sleep(60)