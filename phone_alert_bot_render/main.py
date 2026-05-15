import os
import requests
import time

# =========================
# TELEGRAM SETUP
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
# FX PRICE (FREE STABLE API)
# =========================
def get_fx(symbol):
    try:
        url = f"https://api.exchangerate.host/latest?base={symbol[:3]}&symbols={symbol[3:]}"
        r = requests.get(url, timeout=10).json()
        return float(r["rates"][symbol[3:]])
    except:
        return None


# =========================
# CRYPTO PRICE
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
fx_symbols = [
    "EURUSD", "GBPUSD", "USDCAD",
    "USDCHF", "USDJPY", "EURJPY", "GBPJPY"
]

crypto_symbols = {
    "BTCUSD": "bitcoin"
}


# =========================
# STORAGE (for structure + liquidity)
# =========================
history = {s: [] for s in fx_symbols}


# =========================
# PHASE 3 ENGINE (LIQUIDITY + MSS)
# =========================
def liquidity_engine(data):
    if len(data) < 5:
        return None, None

    recent_high = max(data[-5:])
    recent_low = min(data[-5:])

    last = data[-1]
    prev = data[-2] if len(data) > 1 else last

    sweep = None
    mss = None

    # liquidity sweep detection
    if last > recent_high:
        sweep = "🔥 BUY-SIDE LIQUIDITY SWEPT"
    elif last < recent_low:
        sweep = "🔥 SELL-SIDE LIQUIDITY SWEPT"

    # MSS logic
    if sweep == "🔥 BUY-SIDE LIQUIDITY SWEPT" and last < prev:
        mss = "📉 MSS BEARISH"
    elif sweep == "🔥 SELL-SIDE LIQUIDITY SWEPT" and last > prev:
        mss = "📈 MSS BULLISH"

    return sweep, mss


# =========================
# MAIN LOOP
# =========================
while True:

    lines = ["📊 PHASE 1 → 3 ICT SCANNER (LIVE)"]

    # =========================
    # FX PROCESS
    # =========================
    for sym in fx_symbols:

        price = get_fx(sym)

        if not price:
            lines.append(f"{sym}: NO DATA")
            continue

        # store history
        history[sym].append(price)

        if len(history[sym]) > 20:
            history[sym].pop(0)

        sweep, mss = liquidity_engine(history[sym])

        msg = f"{sym}: {price:.5f}"

        if sweep:
            msg += f" → {sweep}"

        if mss:
            msg += f" → {mss}"

        lines.append(msg)

    # =========================
    # CRYPTO PROCESS
    # =========================
    for name, coin in crypto_symbols.items():

        price = get_crypto(coin)

        if price:
            lines.append(f"{name}: {price:.2f} → 📈 ACTIVE")
        else:
            lines.append(f"{name}: NO DATA")

    send_message("\n".join(lines))

    time.sleep(300)
