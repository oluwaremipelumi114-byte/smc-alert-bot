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
# PRICE SOURCE (simple + stable)
# =========================
def get_price(symbol):
    try:
        url = f"https://api.exchangerate.host/latest?base={symbol[:3]}&symbols={symbol[3:]}"
        r = requests.get(url, timeout=10).json()
        return float(r["rates"][symbol[3:]])
    except:
        return None


# =========================
# CRYPTO
# =========================
def get_crypto_price(coin):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
        r = requests.get(url, timeout=10).json()
        return float(r[coin]["usd"])
    except:
        return None


# =========================
# 🧠 LIQUIDITY ENGINE
# =========================
def detect_liquidity(prices):
    if len(prices) < 5:
        return None, None

    highs = max(prices[-5:])
    lows = min(prices[-5:])

    return highs, lows


def detect_sweep(price, prev_high, prev_low):
    sweep = None

    if price > prev_high:
        sweep = "🔥 BUY-SIDE LIQUIDITY SWEPT"
    elif price < prev_low:
        sweep = "🔥 SELL-SIDE LIQUIDITY SWEPT"

    return sweep


def detect_mss(price, prev_price, sweep):
    if not sweep:
        return None

    if "BUY-SIDE" in sweep and price < prev_price:
        return "📉 MSS BEARISH CONFIRMED"

    if "SELL-SIDE" in sweep and price > prev_price:
        return "📈 MSS BULLISH CONFIRMED"

    return None


# =========================
# SYMBOLS
# =========================
forex = ["EURUSD", "GBPUSD", "USDCAD", "USDCHF", "USDJPY", "EURJPY", "GBPJPY"]

crypto = {
    "BTCUSD": "bitcoin"
}


# store history
history = {sym: [] for sym in forex}


# =========================
# MAIN LOOP
# =========================
while True:

    lines = ["📊 PHASE 3: LIQUIDITY + MSS ENGINE"]

    # ---------- FOREX ----------
    for symbol in forex:

        price = get_price(symbol)

        if not price:
            lines.append(f"{symbol}: NO DATA")
            continue

        history[symbol].append(price)

        if len(history[symbol]) > 20:
            history[symbol].pop(0)

        prev_high, prev_low = detect_liquidity(history[symbol])

        sweep = detect_sweep(price, prev_high, prev_low)
        mss = detect_mss(price, history[symbol][-2] if len(history[symbol]) > 1 else price, sweep)

        msg = f"{symbol}: {price:.5f}"

        if sweep:
            msg += f" → {sweep}"

        if mss:
            msg += f" → {mss}"

        lines.append(msg)

    # ---------- CRYPTO ----------
    for name, coin in crypto.items():

        price = get_crypto_price(coin)

        if price:
            lines.append(f"{name}: {price:.2f} → MARKET ACTIVE")
        else:
            lines.append(f"{name}: NO DATA")

    send_message("\n".join(lines))

    time.sleep(300)
