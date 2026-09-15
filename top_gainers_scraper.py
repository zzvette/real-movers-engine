# top_gainers_scraper.py

import requests

HEADERS = {"User-Agent": "Mozilla/5.0"}

YAHOO_GAINERS_URL = (
    "https://query1.finance.yahoo.com/v1/finance/screener/predefined/"
    "day_gainers?count=50&offset=0"
)


def fetch_top_gainers(limit: int = 10):
    """
    Pull top gainers from Yahoo Finance's official 'day_gainers' screener.

    Returns a list of dicts:
    [
        {
            "symbol": "NVDA",
            "price": 123.45,
            "change": 8.23,
            "change_pct": 7.12,
            "volume": 45678900,
            "score": 82
        },
        ...
    ]
    """

    try:
        resp = requests.get(YAHOO_GAINERS_URL, headers=HEADERS, timeout=10)
        data = resp.json()
        quotes = data["finance"]["result"][0]["quotes"]
    except Exception:
        return []

    results = []

    for q in quotes:
        try:
            symbol = q.get("symbol")
            price = q.get("regularMarketPrice")
            change = q.get("regularMarketChange")
            change_pct = q.get("regularMarketChangePercent")
            volume = q.get("regularMarketVolume")

            # Reject invalid entries
            if (
                not symbol
                or price is None
                or change is None
                or change_pct is None
                or volume is None
            ):
                continue

            # Simple score heuristic (same logic used in reversal_engine)
            pct_component = max(min(change_pct * 2, 60), -20)
            vol_component = min(volume / 1_000_000, 40)
            score = int(max(min(pct_component + vol_component, 100), 0))

            results.append(
                {
                    "symbol": symbol,
                    "price": price,
                    "change": change,
                    "change_pct": change_pct,
                    "volume": volume,
                    "score": score,
                }
            )

        except Exception:
            continue

    # Sort by percent change
    results.sort(key=lambda x: x["change_pct"], reverse=True)

    return results[:limit]
