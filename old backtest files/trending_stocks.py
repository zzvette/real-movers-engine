import requests

URL = "https://query2.finance.yahoo.com/v1/finance/trending/US"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def fetch_trending(limit=25):
    try:
        resp = requests.get(URL, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print("Error:", e)
        return []

    try:
        quotes = data["finance"]["result"][0]["quotes"]
    except Exception:
        print("Trending list not found.")
        return []

    results = []

    for q in quotes[:limit]:
        results.append({
            "symbol": q.get("symbol"),
            "price": q.get("regularMarketPrice"),
            "change": q.get("regularMarketChange"),
            "change_pct": q.get("regularMarketChangePercent"),
            "volume": q.get("regularMarketVolume"),
            "market_cap": q.get("marketCap")
        })

    return results


if __name__ == "__main__":
    trending = fetch_trending()

    print("\n=== TRENDING STOCKS (Yahoo Finance) ===")
    for t in trending:
        print(t)
