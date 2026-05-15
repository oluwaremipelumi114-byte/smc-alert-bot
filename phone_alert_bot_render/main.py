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

lines = ["📊 Scanner online"]
for name, ticker in symbols.items():
    data = yf.download(ticker, interval="1h", period="2d", progress=False)
    price = float(data["Close"].dropna().iloc[-1])
    lines.append(f"{name}: {price}")

send_message("\n".join(lines))
