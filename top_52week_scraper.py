import requests

HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch_52week_gainers(limit=5):
    """
    Pulls stocks near their 52-week highs using Yahoo's quote API.
    Returns a list of dicts with symbol, price, change_pct, volume, fifty_two_high.
    """

    # First pull a broad universe (same as gainers)
    url = (
        "https://query1.finance.yahoo.com/v1/finance/screener/predefined/"
        "day_gainers?count=200&offset=0"
    )

    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        data = resp.json()
        quotes = data["finance"]["result"][0]["quotes"]
    except Exception:
        return []

    results = []

    for q in quotes:
        try:
            symbol = q.get("symbol")
            price = q.get("regularMarketPrice")
            change_pct = q.get("regularMarketChangePercent")
            volume = q.get("regularMarketVolume")
            fifty_two_high = q.get("fiftyTwoWeekHigh")

            # Reject invalid entries
            if (
                not symbol or
                price is None or
                change_pct is None or
                volume is None or
                fifty_two_high is None
            ):
                continue

            # Only include stocks within 5% of their 52-week high
            if fifty_two_high > 0 and price >= 0.95 * fifty_two_high:
                results.append({
                    "symbol": symbol,
                    "price": price,
                    "change_pct": change_pct,
                    "volume": volume,
                    "fifty_two_high": fifty_two_high
                })

        except Exception:
            continue

    # Sort by percent change
    results.sort(key=lambda x: x["change_pct"], reverse=True)

    return results[:limit]
