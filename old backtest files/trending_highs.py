import requests
import yfinance as yf
import json
from datetime import datetime, UTC

TRENDING_URL = "https://query2.finance.yahoo.com/v1/finance/trending/US"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def fetch_trending_symbols(limit=25):
    try:
        resp = requests.get(TRENDING_URL, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        quotes = data["finance"]["result"][0]["quotes"]
        return [q["symbol"] for q in quotes[:limit]]
    except Exception as e:
        print("Error fetching trending symbols:", e)
        return []

def fetch_quotes(symbols):
    results = []

    for sym in symbols:
        try:
            t = yf.Ticker(sym)
            info = t.info

            price = info.get("currentPrice")
            change_pct = info.get("regularMarketChangePercent")
            volume = info.get("regularMarketVolume")
            high_52 = info.get("fiftyTwoWeekHigh")
            low_52 = info.get("fiftyTwoWeekLow")

            # Skip symbols with missing high/low (crypto, indices, broken tickers)
            if price is None or high_52 is None or low_52 is None:
                continue

            results.append({
                "symbol": sym,
                "price": price,
                "change_pct": change_pct,
                "volume": volume,
                "high_52": high_52,
                "low_52": low_52,
                "dist_to_high_pct": round((price / high_52) * 100, 2)
            })

        except Exception:
            continue

    return results

def fetch_trending_highs(limit=10):
    symbols = fetch_trending_symbols()
    quotes = fetch_quotes(symbols)

    highs = []

    for q in quotes:
        # Must have decent volume
        if (q["volume"] or 0) < 500000:
            continue

        # Near-high band: 97% to 100%
        if q["dist_to_high_pct"] >= 97:
            highs.append(q)

    # Sort by closeness to high, then by change %
    highs.sort(key=lambda x: (x["dist_to_high_pct"], x["change_pct"] or 0), reverse=True)

    return highs[:limit]

def save_json(path, payload):
    with open(path, "w") as f:
        json.dump(payload, f, indent=4)

def run_engine():
    timestamp = datetime.now(UTC).isoformat()

    highs = fetch_trending_highs(limit=10)

    save_json("trending_highs.json", {
        "timestamp": timestamp,
        "highs": highs
    })

    print("\nEngine complete.")
    print(f"Trending highs: {len(highs)}")

if __name__ == "__main__":
    run_engine()
