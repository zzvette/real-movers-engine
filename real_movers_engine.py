import requests
import json
import time
from datetime import datetime

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
SOURCES = [
    {
        "name": "Yahoo",
        "url": "https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}"
    },
    {
        "name": "Finviz",
        "url": "https://finviz.com/api/quote.ashx?t={symbol}"
    }
]

SYMBOLS = [
    "AAPL", "TSLA", "NVDA", "AMD", "META", "AMZN", "MSFT", "NFLX",
    "PLTR", "SMCI", "COIN", "UBER", "SHOP", "SQ", "ROKU", "BABA",
    "NIO", "RIVN", "CVNA", "AI"
]

OUTPUT_FILE = "real_movers.json"

# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------
def fetch_yahoo(symbol):
    try:
        url = SOURCES[0]["url"].format(symbol=symbol)
        r = requests.get(url, timeout=10)
        data = r.json()

        quote = data["quoteResponse"]["result"][0]

        return {
            "Price": quote.get("regularMarketPrice", 0),
            "Change": quote.get("regularMarketChange", 0),
            "Change %": quote.get("regularMarketChangePercent", 0),
            "Volume": quote.get("regularMarketVolume", 0)
        }
    except:
        return None

def fetch_finviz(symbol):
    try:
        url = SOURCES[1]["url"].format(symbol=symbol)
        r = requests.get(url, timeout=10)
        data = r.json()

        return {
            "Price": float(data.get("price", 0)),
            "Change": float(data.get("change", 0)),
            "Change %": float(data.get("change_pct", 0)),
            "Volume": float(data.get("volume", 0))
        }
    except:
        return None

def score_mover(meta):
    score = 0

    try:
        price = float(meta.get("Price", 0))
        change_pct = float(meta.get("Change %", 0))
        volume = float(meta.get("Volume", 0))
    except:
        return 0

    # Price scoring
    if price > 20:
        score += 10
    if price > 50:
        score += 10

    # Momentum scoring
    if change_pct > 2:
        score += 15
    if change_pct > 5:
        score += 20
    if change_pct > 10:
        score += 30

    # Volume scoring
    if volume > 1_000_000:
        score += 10
    if volume > 5_000_000:
        score += 15
    if volume > 10_000_000:
        score += 20

    return score

# ---------------------------------------------------------
# MAIN ENGINE
# ---------------------------------------------------------
def run_engine():
    movers = []

    for symbol in SYMBOLS:
        meta = {}
        sources_used = []

        yahoo = fetch_yahoo(symbol)
        if yahoo:
            meta.update(yahoo)
            sources_used.append("Yahoo")

        finviz = fetch_finviz(symbol)
        if finviz:
            meta.update(finviz)
            sources_used.append("Finviz")

        if not meta:
            continue

        score = score_mover(meta)

        movers.append({
            "symbol": symbol,
            "meta": meta,
            "score": score,
            "sources": sources_used,
            "timestamp": datetime.utcnow().isoformat()
        })

        time.sleep(1)

    movers_sorted = sorted(movers, key=lambda x: x["score"], reverse=True)

    output = {
        "generated": datetime.utcnow().isoformat(),
        "movers": movers_sorted
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=4)

    print("Real Movers JSON generated successfully.")

# ---------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------
if __name__ == "__main__":
    run_engine()
