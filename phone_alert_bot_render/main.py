import os
import requests
import yfinance as yf

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    requests.post(url, data=payload)


symbols = {
    "XAUUSD": "GC=F",
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    "USDCAD": "USDCAD=X",
    "USDCHF": "USDCHF=X",
    "BTCUSD": "BTC-USD",
    "EURAUD": "EURAUD=X",
    "EURJPY": "EURJPY=X",
    "USDJPY": "USDJPY=X",
    "GBPJPY": "GBPJPY=X"
}


# =========================
# 🧠 MARKET STRUCTURE ENGINE
# =========================
def get_structure(data):
    highs = data["High"]
    lows = data["Low"]

    if len(data) < 20:
        return "NO DATA"

    recent_highs = highs.iloc[-10:-1]
    recent_lows = lows.iloc[-10:-1]

    last_high = highs.iloc[-1]
    last_low = lows.iloc[-1]

    bullish_bos = last_high > recent_highs.max()
    bearish_bos = last_low < recent_lows.min()

    if bullish_bos:
        return "📈 BULLISH (BOS UP)"
    elif bearish_bos:
        return "📉 BEARISH (BOS DOWN)"
    else:
        return "🔁 RANGE"


# =========================
# 📊 MAIN LOOP
# =========================
lines = ["📊 STRUCTURE SCANNER ONLINE"]

for name, ticker in symbols.items():
    try:
        data = yf.download(
            ticker,
            interval="1h",
            period="5d",
            progress=False,
            threads=False
        )

        # 🚨 SAFE CHECKS
        if data is None or data.empty:
            lines.append(f"{name}: NO DATA")
            continue

        close = data["Close"].dropna()

        if close.empty:
            lines.append(f"{name}: NO CLOSE DATA")
            continue

        price = float(close.iloc[-1])

        structure = get_structure(data)

        lines.append(f"{name}: {price:.2f} → {structure}")

    except Exception:
        lines.append(f"{name}: ERROR")

send_message("\n".join(lines))
