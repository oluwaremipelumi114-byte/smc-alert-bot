import os
import requests
import time

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": text})
    except:
        pass


# =========================
# FX (STABLE - ECB DATA)
# =========================
def get_fx(base, quote):
    try:
        url = f"https://api.frankfurter.app/latest?from={base}&to={quote}"
        r = requests.get(url, timeout=10).json()
        return float(r["rates"][quote])
    except:
        return None


# =========================
# CRYPTO
# =========================
def get_crypto(coin):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
        r = requests.get(url, timeout=10).json()
        return float(r[coin]["usd"])
    except:
        return None


# =========================
# SYMBOLS
# =========================
fx_pairs = {
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
# HISTORY STORAGE
# =========================
history = {k: [] for k in fx_pairs}


# =========================
# LIQUIDITY ENGINE (REAL FIXED LOGIC)
# =========================
def liquidity_engine(data):
    if len(data) < 5:
        return None, None

    recent_high = max(data[-5:])
    recent_low = min(data[-5:])

    last = data[-1]
    prev = data[-2]

    sweep = None
    mss = None

    if last > recent_high:
        sweep = "🔥 BUY-SIDE LIQUIDITY SWEPT"
    elif last < recent_low:
        sweep = "🔥 SELL-SIDE LIQUIDITY SWEPT"

    if sweep == "🔥 BUY-SIDE LIQUIDITY SWEPT" and last < prev:
        mss = "📉 MSS BEARISH"
    elif sweep == "🔥 SELL-SIDE LIQUIDITY SWEPT" and last > prev:
        mss = "📈 MSS BULLISH"

    return sweep, mss


# =========================
# MAIN LOOP
# =========================
while True:

    lines = ["📊 ICT LIQUIDITY SCANNER (STABLE VERSION)"]

    # FX
    for pair, (base, quote) in fx_pairs.items():

        price = get_fx(base, quote)

        if price is None:
            lines.append(f"{pair}: NO DATA")
            continue

        history[pair].append(price)

        if len(history[pair]) > 20:
            history[pair].pop(0)

        sweep, mss = liquidity_engine(history[pair])

        msg = f"{pair}: {price:.5f}"

        if sweep:
            msg += f" → {sweep}"

        if mss:
            msg += f" → {mss}"

        lines.append(msg)

    # CRYPTO
    for name, coin in crypto.items():

        price = get_crypto(coin)

        if price:
            lines.append(f"{name}: {price:.2f} → 📈 ACTIVE")
        else:
            lines.append(f"{name}: NO DATA")

    send_message("\n".join(lines))

    time.sleep(300)
