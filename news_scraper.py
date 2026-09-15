# news_scraper.py

import requests

HEADERS = {"User-Agent": "Mozilla/5.0"}

# Yahoo Finance news feed (official JSON)
YAHOO_NEWS_URL = (
    "https://query1.finance.yahoo.com/v1/finance/news?category=generalnews"
)


def fetch_news_catalysts(limit: int = 20):
    """
    Pull news headlines from Yahoo Finance and extract tickers.

    Returns a list of dicts:
    [
        {
            "symbol": "TSLA",
            "headline": "Tesla jumps after strong delivery numbers"
        },
        ...
    ]
    """

    try:
        resp = requests.get(YAHOO_NEWS_URL, headers=HEADERS, timeout=10)
        data = resp.json()
        items = data.get("items", [])
    except Exception:
        return []

    results = []

    for item in items:
        try:
            headline = item.get("title")
            related = item.get("relatedTickers", [])

            if not headline or not related:
                continue

            # Attach headline to each related ticker
            for sym in related:
                results.append(
                    {
                        "symbol": sym,
                        "headline": headline,
                    }
                )

        except Exception:
            continue

    # Deduplicate by symbol
    seen = set()
    unique_results = []

    for r in results:
        if r["symbol"] not in seen:
            seen.add(r["symbol"])
            unique_results.append(r)

    return unique_results[:limit]
