import requests

HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch_top_gainers(limit=5):
    """
    Pulls top gainers from Yahoo Finance's day_gainers screener.
    Returns a list of dicts with symbol, price, change_pct, volume.
    """

    url = (
        "https://query1.finance.yahoo.com/v1/finance/screener/predefined/"
        "day_gainers?count=100&offset=0"
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
            symbol = q.get("symbol")
            price = q.get("regularMarketPrice")
            change_pct = q.get("regularMarketChangePercent")
            volume = q.get("regularMarketVolume")

            # Reject invalid entries
            if not symbol or price is None or change_pct is None or volume is None:
                continue

            gainers.append({
                "symbol": symbol,
                "price": price,
                "change_pct": change_pct,
                "volume": volume,
            })
        except Exception:
            continue

    # Sort by percent change
    gainers.sort(key=lambda x: x["change_pct"], reverse=True)

    return gainers[:limit]
