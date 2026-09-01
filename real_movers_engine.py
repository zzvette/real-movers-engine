import json
import time
from datetime import datetime
import requests
import yfinance as yf

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
NASDAQ_URL = "https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=5000"
OUTPUT_FILE = "real_movers.json"

# Minimum requirements for low-cap movers
MIN_PRICE = 1.00
MAX_PRICE = 15.00
MIN_VOLUME = 300_000
MAX_MARKET_CAP = 2_000_000_000  # 2B

# ---------------------------------------------------------
# FETCH NASDAQ UNIVERSE
# ---------------------------------------------------------
def fetch_nasdaq_universe():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    try:
        r = requests.get(NASDAQ_URL, headers=headers, timeout=15)
        data = r.json()

        rows = data["data"]["table"]["rows"]
        tickers = []

        for row in rows:
            symbol = row.get("symbol", "").strip()
            name = row.get("name", "").strip()
            market_cap = row.get("marketCap", "0").replace(",", "")

            # Skip ETFs, warrants, preferred shares
            if any(x in name.upper() for x in ["ETF", "ETN", "FUND", "PREFERRED", "WARRANT"]):
                continue

            # Skip OTC
            if row.get("exchange", "").upper() == "OTC":
                continue

            # Market cap filter
            try:
                mc = float(market_cap)
                if mc > MAX_MARKET_CAP:
                    continue
            except:
                continue

            tickers.append(symbol)

        print(f"DEBUG: NASDAQ universe size after filtering: {len(tickers)}")
        return tickers

    except Exception as e:
        print(f"DEBUG: Failed to fetch NASDAQ universe: {e}")
        return []

# ---------------------------------------------------------
# SCORING LOGIC
# ---------------------------------------------------------
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
    if price > 5:
        score += 10
    if price > 10:
        score += 10

    # Momentum scoring
    if change_pct > 2:
        score += 15
    if change_pct > 5:
        score += 20
    if change_pct > 10:
        score += 30

    # Volume scoring
    if volume > 500_000:
        score += 10
    if volume > 1_000_000:
        score += 15
    if volume > 5_000_000:
        score += 20

    return score

# ---------------------------------------------------------
# MAIN ENGINE
# ---------------------------------------------------------
def run_engine():
    print("DEBUG: Fetching NASDAQ universe...")
    universe = fetch_nasdaq_universe()

    print("DEBUG: Total tickers to scan:", len(universe))

    movers = []

    for symbol in universe:
        print(f"\nDEBUG: Processing {symbol}")

        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
        except Exception as e:
            print(f"DEBUG: yfinance failed for {symbol}: {e}")
            continue

        price = info.get("currentPrice", 0)
        volume = info.get("volume", 0)

        # Basic filters
        if price is None or price < MIN_PRICE or price > MAX_PRICE:
            print(f"DEBUG: Price filter fail for {symbol}: {price}")
            continue

        if volume is None or volume < MIN_VOLUME:
            print(f"DEBUG: Volume filter fail for {symbol}: {volume}")
            continue

        meta = {
            "Price": price,
            "Change": info.get("regularMarketChange", 0),
            "Change %": info.get("regularMarketChangePercent", 0),
            "Volume": volume
        }

        print(f"DEBUG: Meta for {symbol}: {meta}")

        score = score_mover(meta)
        print(f"DEBUG: Score for {symbol}: {score}")

        movers.append({
            "symbol": symbol,
            "meta": meta,
            "score": score,
            "sources": ["NASDAQ", "yfinance"],
            "timestamp": datetime.utcnow().isoformat()
        })

        time.sleep(0.5)

    print("\nDEBUG: Raw movers count:", len(movers))

    # Sort by score
    movers_sorted = sorted(movers, key=lambda x: x["score"], reverse=True)

    # Top 10 only
    top10 = movers_sorted[:10]
    print("DEBUG: Top 10 movers:", top10)

    output = {
        "generated": datetime.utcnow().isoformat(),
        "movers": top10
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
