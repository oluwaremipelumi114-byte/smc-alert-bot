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
# FOREX (FIXED - FREE & STABLE)
# =========================
def get_forex_price(base, quote):
    try:
        url = f"https://api.exchangerate.host/convert?from={base}&to={quote}"
        r = requests.get(url, timeout=10).json()
        return float(r["result"])
    except:
        return None


# =========================
# CRYPTO (CoinGecko)
# =========================
def get_crypto_price(coin):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
        r = requests.get(url, timeout=10).json()
        return float(r[coin]["usd"])
    except:
        return None


# =========================
# STRUCTURE (simple)
# =========================
def structure(price, prev):
    if price is None or prev is None:
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
    "EURUSD": ("EUR", "USD"),
    "GBPUSD": ("GBP", "USD"),
    "USDCAD": ("USD", "CAD"),
    "USDCHF": ("USD", "CHF"),
    "USDJPY": ("USD", "JPY"),
    "EURJPY": ("EUR", "JPY"),
    "GBPJPY": ("GBP", "JPY")
}

crypto = {
    "BTCUSD": "bitcoin"
}


# =========================
# MAIN LOOP
# =========================
while True:

    lines = ["📊 STRUCTURE SCANNER (LIVE FIXED)"]

    # ---------- FOREX ----------
    for name, pair in forex.items():
        base, quote = pair

        price = get_forex_price(base, quote)
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

    time.sleep(300)
