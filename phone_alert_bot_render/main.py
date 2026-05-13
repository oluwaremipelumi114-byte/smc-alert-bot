import os,time,requests
from dotenv import load_dotenv
load_dotenv()
API=os.getenv("TWELVE_DATA_KEY")
BOT=os.getenv("TELEGRAM_BOT_TOKEN")
CHAT=os.getenv("TELEGRAM_CHAT_ID")
PAIRS=["XAU/USD","EUR/USD","GBP/USD","USD/CAD","USD/CHF"]
def send(m):
    if not BOT or not CHAT: print(m); return
    requests.post(f"https://api.telegram.org/bot{BOT}/sendMessage", data={"chat_id":CHAT,"text":m}, timeout=10)
def fetch(symbol):
    u=f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1h&outputsize=5&apikey={API}"
    return requests.get(u, timeout=20).json().get("values",[])
while True:
    for p in PAIRS:
        vals=fetch(p)
        if len(vals)>=2:
            if float(vals[0]["close"])>float(vals[1]["close"])*1.002:
                send(f"{p} bullish setup detected.\nPotential RR: 1:5\n\n/buy\n/ignore")
        time.sleep(2)
    time.sleep(300)
