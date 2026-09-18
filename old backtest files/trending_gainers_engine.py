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

            if price is None or change_pct is None:
                continue

            results.append({
                "symbol": sym,
                "price": price,
                "change_pct": change_pct,
                "volume": volume
            })

        except Exception:
            continue

    return results

def fetch_trending_gainers(limit=10):
    symbols = fetch_trending_symbols()
    quotes = fetch_quotes(symbols)
    quotes.sort(key=lambda x: x["change_pct"], reverse=True)
    return quotes[:limit]

def save_json(path, payload):
    with open(path, "w") as f:
        json.dump(payload, f, indent=4)

def run_engine():
    timestamp = datetime.now(UTC).isoformat()

    trending_symbols = fetch_trending_symbols()
    trending_quotes = fetch_quotes(trending_symbols)
    trending_gainers = fetch_trending_gainers()

    save_json("trending.json", {
        "timestamp": timestamp,
        "symbols": trending_symbols,
        "quotes": trending_quotes
    })

    save_json("trending_gainers.json", {
        "timestamp": timestamp,
        "gainers": trending_gainers
    })

    save_json("daily_screener.json", {
        "timestamp": timestamp,
        "signals": {
            "trending": trending_quotes,
            "gainers": trending_gainers
        }
    })

    print("\nEngine complete.")
    print(f"Trending symbols: {len(trending_symbols)}")
    print(f"Trending quotes: {len(trending_quotes)}")
    print(f"Gainers: {len(trending_gainers)}")

if __name__ == "__main__":
    run_engine()
