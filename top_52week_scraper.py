# top_52week_scraper.py

import requests

HEADERS = {"User-Agent": "Mozilla/5.0"}

# We pull a broad universe from Yahoo's gainers list,
# then filter for stocks near their 52-week highs.
YAHOO_GAINERS_URL = (
    "https://query1.finance.yahoo.com/v1/finance/screener/predefined/"
    "day_gainers?count=200&offset=0"
)


def fetch_52week_gainers(limit: int = 10):
    """
    Pull stocks trading near their 52-week highs using Yahoo Finance's quote API.

    Returns a list of dicts:
    [
        {
            "symbol": "AAPL",
            "price": 189.23,
            "change": 3.12,
            "change_pct": 1.68,
            "volume": 45678900,
            "score": 74
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
            fifty_two_high = q.get("fiftyTwoWeekHigh")

            # Reject invalid entries
            if (
                not symbol
                or price is None
                or change is None
                or change_pct is None
                or volume is None
                or fifty_two_high is None
            ):
                continue

            # Only include stocks within 5% of their 52-week high
            if fifty_two_high > 0 and price >= 0.95 * fifty_two_high:

                # Same scoring logic used in reversal_engine + gainers scraper
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
