# top_52week_scraper.py

import requests

HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch_52week_gainers(limit=5):
    """
    Pulls 52-week high gainers from Yahoo Finance.
    """

    url = (
        "https://query1.finance.yahoo.com/v1/finance/screener/predefined/"
        "day_gainers?count=50&offset=0"
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
            fifty_two_high = q.get("fiftyTwoWeekHigh", None)
            price = q.get("regularMarketPrice", 0.0)

            if fifty_two_high and price >= 0.95 * fifty_two_high:
                gainers.append({
                    "symbol": q["symbol"],
                    "price": price,
                    "change_pct": q.get("regularMarketChangePercent", 0.0),
                    "volume": q.get("regularMarketVolume", 0),
                    "fifty_two_high": fifty_two_high,
                })
        except Exception:
            continue

    gainers.sort(key=lambda x: x["change_pct"], reverse=True)

    return gainers[:limit]
