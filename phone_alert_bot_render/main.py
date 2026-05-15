import os
import requests
import time

# =========================
# CONFIG
# =========================
API_KEY = os.getenv("TWELVE_API_KEY")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# =========================
# TELEGRAM
# =========================
def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": text})
    except:
        pass


# =========================
# CANDLE DATA (REAL MARKET DATA)
# =========================
def get_candles(symbol):
    try:
        url = (
            f"https://api.twelvedata.com/time_series"
            f"?symbol={symbol}"
            f"&interval=1h"
            f"&outputsize=50"
            f"&apikey={API_KEY}"
        )

        r = requests.get(url, timeout=10).json()

        if "values" not in r:
            return None

        candles = r["values"]

        highs = [float(c["high"]) for c in candles]
        lows = [float(c["low"]) for c in candles]
        closes = [float(c["close"]) for c in candles]

        return highs, lows, closes

    except:
        return None


# =========================
# STRUCTURE ENGINE
# =========================
def structure(highs, lows, closes):
    if len(highs) < 10:
        return "NO DATA"

    recent_high = max(highs[:10])
    recent_low = min(lows[:10])

    last_close = closes[0]
    prev_close = closes[1]

    # Basic structure shift
    if last_close > recent_high:
        return "📈 BULLISH BREAK OF STRUCTURE"
    elif last_close < recent_low:
        return "📉 BEARISH BREAK OF STRUCTURE"
    else:
        return "🔁 RANGE / CONSOLIDATION"


# =========================
# SYMBOLS (TwelveData format)
# =========================
symbols = {
    "EUR/USD": "EUR/USD",
    "GBP/USD": "GBP/USD",
    "USD/CAD": "USD/CAD",
    "USD/CHF": "USD/CHF",
    "USD/JPY": "USD/JPY",
    "EUR/JPY": "EUR/JPY",
    "GBP/JPY": "GBP/JPY"
}


# =========================
# MAIN LOOP
# =========================
while True:

    lines = ["📊 REAL CANDLE STRUCTURE ENGINE (PHASE 4 READY BASE)"]

    for name, symbol in symbols.items():

        data = get_candles(symbol)

        if not data:
            lines.append(f"{name}: NO DATA")
            continue

        highs, lows, closes = data

        state = structure(highs, lows, closes)

        lines.append(f"{name}: {state}")

    send_message("\n".join(lines))

    time.sleep(300)
