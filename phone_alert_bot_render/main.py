import os
import requests
import time

# =========================
# TELEGRAM
# =========================
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": text})
    except:
        pass


# =========================
# FOREX (OHLC CANDLES - FIXED)
# =========================
def get_candles(symbol):
    try:
        url = f"https://api.frankfurter.app/latest?from={symbol[:3]}&to={symbol[3:]}"
        r = requests.get(url, timeout=10).json()

        price = float(r["rates"][symbol[3:]])

        # fake OHLC approximation (API limitation workaround)
        return {
            "high": price * 1.001,
            "low": price * 0.999,
            "close": price
        }
    except:
        return None


# =========================
# CRYPTO (simple price feed)
# =========================
def get_crypto_price(coin):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
        r = requests.get(url, timeout=10).json()
        return float(r[coin]["usd"])
    except:
        return None


# =========================
# 🧠 STRUCTURE ENGINE (REAL LOGIC)
# =========================
def structure(symbol, candles, prev_high, prev_low):
    if not candles:
        return "NO DATA", None, None

    high = candles["high"]
    low = candles["low"]

    bos = "RANGE"

    if high > prev_high and low > prev_low:
        bos = "📈 BULLISH BOS"
    elif high < prev_high and low < prev_low:
        bos = "📉 BEARISH BOS"

    return bos, high, low


# =========================
# SYMBOLS
# =========================
forex = ["EURUSD", "GBPUSD", "USDCAD", "USDCHF", "USDJPY", "EURJPY", "GBPJPY"]

crypto = {
    "BTCUSD": "bitcoin"
}


# =========================
# MAIN LOOP
# =========================
while True:

    lines = ["📊 PHASE 2 STRUCTURE ENGINE (CANDLE MODE)"]

    # store previous structure levels
    prev_highs = {}
    prev_lows = {}

    # ---------- FOREX ----------
    for symbol in forex:

        candles = get_candles(symbol)

        prev_high = prev_highs.get(symbol, 1)
        prev_low = prev_lows.get(symbol, 0)

        bos, high, low = structure(symbol, candles, prev_high, prev_low)

        if candles:
            prev_highs[symbol] = high
            prev_lows[symbol] = low

            lines.append(f"{symbol}: {candles['close']:.5f} → {bos}")
        else:
            lines.append(f"{symbol}: NO DATA")

    # ---------- CRYPTO ----------
    for name, coin in crypto.items():

        price = get_crypto_price(coin)

        if price:
            lines.append(f"{name}: {price:.2f} → 📈 MARKET ACTIVE")
        else:
            lines.append(f"{name}: NO DATA")

    send_message("\n".join(lines))

    time.sleep(300)
