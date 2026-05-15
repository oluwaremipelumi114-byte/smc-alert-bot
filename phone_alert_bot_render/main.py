import os
import requests
import time

# =========================
# 🔑 KEYS
# =========================
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TWELVE_API_KEY = os.getenv("TWELVE_API_KEY")


# =========================
# 📲 TELEGRAM
# =========================
def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": text})
    except:
        pass


# =========================
# 🌐 DATA (Twelve Data)
# =========================
def get_forex_price(symbol):
    try:
        url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={TWELVE_API_KEY}"
        r = requests.get(url, timeout=10).json()
        return float(r["price"])
    except:
        return None


def get_crypto_price(coin):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
        r = requests.get(url, timeout=10).json()
        return float(r[coin]["usd"])
    except:
        return None


# =========================
# 🧠 SIMPLE STRUCTURE
# =========================
def structure(price, prev):
    if not price or not prev:
        return "NO DATA"
    if price > prev:
        return "📈 BULLISH"
    elif price < prev:
        return "📉 BEARISH"
    return "🔁 RANGE"


# =========================
# SYMBOLS
# =========================
forex = {
    "EURUSD": "EUR/USD",
    "GBPUSD": "GBP/USD",
    "USDCAD": "USD/CAD",
    "USDCHF": "USD/CHF",
    "USDJPY": "USD/JPY",
    "EURJPY": "EUR/JPY",
    "GBPJPY": "GBP/JPY"
}

crypto = {
    "BTCUSD": "bitcoin"
}


# =========================
# 🚀 MAIN LOOP (RAILWAY SAFE)
# =========================
while True:

    lines = ["📊 STRUCTURE SCANNER (LIVE)"]

    # ---------- FOREX ----------
    for name, symbol in forex.items():
        price = get_forex_price(symbol)
        prev = price * 0.999 if price else None

        state = structure(price, prev)

        if price:
            lines.append(f"{name}: {price:.5f} → {state}")
        else:
            lines.append(f"{name}: NO DATA")

    # ---------- CRYPTO ----------
    for name, coin in crypto.items():
        price = get_crypto_price(coin)
        prev = price * 0.999 if price else None

        state = structure(price, prev)

        if price:
            lines.append(f"{name}: {price:.2f} → {state}")
        else:
            lines.append(f"{name}: NO DATA")

    send_message("\n".join(lines))

    # ⏱ avoid API spam + Railway limits
    time.sleep(300)  # every 5 minutes
