# top_gainers_scraper.py

import requests

HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch_top_gainers(limit=5):
    """
    Pulls top gainers from Yahoo Finance's public screener API.
    Returns a list of dicts with symbol, price, change_pct, volume.
    """

    url = (
        "https://query1.finance.yahoo.com/v1/finance/screener/predefined/"
        "most_actives?count=50&offset=0"
    )

    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        data = resp.json()
        quotes = data["finance"]["result"][0]["quotes"]
    except Exception:
        return []

    gainers = []
    for q in quotes:
        try:
            gainers.append({
                "symbol": q["symbol"],
                "price": q.get("regularMarketPrice", 0.0),
                "change_pct": q.get("regularMarketChangePercent", 0.0),
                "volume": q.get("regularMarketVolume", 0),
            })
        except Exception:
            continue

    # Sort by percent change
    gainers.sort(key=lambda x: x["change_pct"], reverse=True)

    return gainers[:limit]
