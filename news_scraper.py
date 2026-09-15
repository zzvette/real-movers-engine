# news_scraper.py (yfinance version)

import yfinance as yf

def fetch_news_catalysts(limit: int = 20):
    try:
        news = yf.get_yf_news()
        if not news:
            return []
    except Exception:
        return []

    results = []

    for item in news[:limit]:
        try:
            headline = item.get("title")
            related = item.get("relatedTickers", [])

            if not headline or not related:
                continue

            for sym in related:
                results.append({"symbol": sym, "headline": headline})
        except Exception:
            continue

    # Deduplicate
    seen = set()
    unique = []

    for r in results:
        if r["symbol"] not in seen:
            seen.add(r["symbol"])
            unique.append(r)

    return unique
