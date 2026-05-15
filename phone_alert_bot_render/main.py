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
# FX DATA
# =========================
def get_fx(base, quote):
    try:
        url = f"https://api.frankfurter.app/latest?from={base}&to={quote}"
        r = requests.get(url, timeout=10).json()
        return float(r["rates"][quote])
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


# =========================
# STRUCTURE STORAGE (FIXED)
# =========================
history = {k: [] for k in fx_pairs}


# =========================
# REAL LIQUIDITY ENGINE (FIXED LOGIC)
# =========================
def liquidity_engine(data):

    if len(data) < 6:
        return None, None

    # OLD structure (previous range)
    prev_high = max(data[-10:-5])
    prev_low = min(data[-10:-5])

    # NEW structure (latest range)
    recent_high = max(data[-5:])
    recent_low = min(data[-5:])

    last = data[-1]
    prev = data[-2]

    sweep = None
    mss = None

    # 🔥 sweep detection (TRUE break + rejection logic)
    if recent_high > prev_high:
        if last < recent_high:
            sweep = "🔥 BUY-SIDE LIQUIDITY SWEPT"

    if recent_low < prev_low:
        if last > recent_low:
            sweep = "🔥 SELL-SIDE LIQUIDITY SWEPT"

    # 📉 MSS logic (real shift confirmation)
    if sweep == "🔥 BUY-SIDE LIQUIDITY SWEPT" and last < prev:
        mss = "📉 MSS BEARISH CONFIRMED"

    if sweep == "🔥 SELL-SIDE LIQUIDITY SWEPT" and last > prev:
        mss = "📈 MSS BULLISH CONFIRMED"

    return sweep, mss


# =========================
# MAIN LOOP
# =========================
while True:

    lines = ["📊 ICT LIQUIDITY ENGINE (FIXED LOGIC)"]

    for pair, (base, quote) in fx_pairs.items():

        price = get_fx(base, quote)

        if price is None:
            lines.append(f"{pair}: NO DATA")
            continue

        history[pair].append(price)

        if len(history[pair]) > 30:
            history[pair].pop(0)

        sweep, mss = liquidity_engine(history[pair])

        msg = f"{pair}: {price:.5f}"

        if sweep:
            msg += f" → {sweep}"

        if mss:
            msg += f" → {mss}"

        lines.append(msg)

    send_message("\n".join(lines))

    time.sleep(300)
