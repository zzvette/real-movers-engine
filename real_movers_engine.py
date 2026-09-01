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
    except Exception as e:
        print(f"DEBUG: Yahoo fetch failed for {symbol}: {e}")
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
    except Exception as e:
        print(f"DEBUG: Finviz fetch failed for {symbol}: {e}")
        return None

def score_mover(meta):
    score = 0

    try:
        price = float(meta.get("Price", 0))
        change_pct = float(meta.get("Change %", 0))
        volume = float(meta.get("Volume", 0))
    except Exception as e:
        print(f"DEBUG: Score calc failed: {e}")
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

    print("DEBUG: Starting engine")
    print("DEBUG: Symbols to scan:", SYMBOLS)

    for symbol in SYMBOLS:
        print(f"\nDEBUG: Processing {symbol}")

        meta = {}
        sources_used = []

        yahoo = fetch_yahoo(symbol)
        print(f"DEBUG: Yahoo data for {symbol}: {yahoo}")
        if yahoo:
            meta.update(yahoo)
            sources_used.append("Yahoo")

        finviz = fetch_finviz(symbol)
        print(f"DEBUG: Finviz data for {symbol}: {finviz}")
        if finviz:
            meta.update(finviz)
            sources_used.append("Finviz")

        print(f"DEBUG: Combined meta for {symbol}: {meta}")

        if not meta:
            print(f"DEBUG: No data for {symbol}, skipping.")
            continue

        score = score_mover(meta)
        print(f"DEBUG: Score for {symbol}: {score}")

        movers.append({
            "symbol": symbol,
            "meta": meta,
            "score": score,
            "sources": sources_used,
            "timestamp": datetime.utcnow().isoformat()
        })

        time.sleep(1)

    print("\nDEBUG: Raw movers list:", movers)

    movers_sorted = sorted(movers, key=lambda x: x["score"], reverse=True)
    print("DEBUG: Sorted movers:", movers_sorted)

    output = {
        "generated": datetime.utcnow().isoformat(),
        "movers": movers_sorted
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=4)

    print("Real Movers JSON generated successfully.")
    print("DEBUG: Output written to real_movers.json")

# ---------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------
if __name__ == "__main__":
    run_engine()
