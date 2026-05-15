import os
import requests
import time

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})


# =========================
# PRICE FEED
# =========================
def get_price(symbol):
    try:
        url = f"https://api.exchangerate.host/latest?base={symbol[:3]}&symbols={symbol[3:]}"
        r = requests.get(url, timeout=10).json()
        return float(r["rates"][symbol[3:]])
    except:
        return None


# =========================
# HISTORY STORAGE
# =========================
symbols = ["EURUSD","GBPUSD","USDCAD","USDCHF","USDJPY","EURJPY","GBPJPY"]

history = {s: [] for s in symbols}


# =========================
# LIQUIDITY LOGIC
# =========================
def sweep_and_mss(data):
    if len(data) < 5:
        return None, None

    recent_high = max(data[-5:])
    recent_low = min(data[-5:])

    last = data[-1]
    prev = data[-2]

    sweep = None
    mss = None

    # sweep logic
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
# LOOP
# =========================
while True:

    lines = ["📊 PHASE 3 LIQUIDITY ENGINE (ACTIVE)"]

    for sym in symbols:

        price = get_price(sym)

        if not price:
            lines.append(f"{sym}: NO DATA")
            continue

        history[sym].append(price)

        if len(history[sym]) > 20:
            history[sym].pop(0)

        sweep, mss = sweep_and_mss(history[sym])

        msg = f"{sym}: {price:.5f}"

        if sweep:
            msg += f" → {sweep}"

        if mss:
            msg += f" → {mss}"

        lines.append(msg)

    send_message("\n".join(lines))

    time.sleep(300)
