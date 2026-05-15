import os
import requests
import yfinance as yf

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    requests.post(url, data=payload)

symbol = "EURUSD=X"

data = yf.download(symbol, interval="1h", period="2d")
last_close = float(data["Close"].dropna().iloc[-1])

send_message(f"Scanner test running ✅\n{symbol} last price: {last_close:.5f}")
