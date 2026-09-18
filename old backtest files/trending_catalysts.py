import requests
import json
from datetime import datetime, UTC

TRENDING_URL = "https://query2.finance.yahoo.com/v1/finance/trending/US"
NEWS_URL = "https://query2.finance.yahoo.com/v1/finance/search?q={symbol}"

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

def fetch_news(symbol):
    try:
        url = NEWS_URL.format(symbol=symbol)
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        items = data.get("news", [])
        catalysts = []

        for item in items:
            title = item.get("title")
            link = item.get("link")
            publisher = item.get("publisher")

            if not title:
                continue

            catalysts.append({
                "title": title,
                "publisher": publisher,
                "link": link
            })

        return catalysts

    except Exception:
        return []

def fetch_trending_catalysts():
    symbols = fetch_trending_symbols()
    results = []

    for sym in symbols:
        catalysts = fetch_news(sym)
        if catalysts:
            results.append({
                "symbol": sym,
                "catalysts": catalysts
            })

    return results

def save_json(path, payload):
    with open(path, "w") as f:
        json.dump(payload, f, indent=4)

def run_engine():
    timestamp = datetime.now(UTC).isoformat()

    catalysts = fetch_trending_catalysts()

    save_json("trending_catalysts.json", {
        "timestamp": timestamp,
        "catalysts": catalysts
    })

    print("\nEngine complete.")
    print(f"Symbols with catalysts: {len(catalysts)}")

if __name__ == "__main__":
    run_engine()
