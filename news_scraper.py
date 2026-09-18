import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

SEARCH_URL = "https://query2.finance.yahoo.com/v1/finance/search?q={symbol}"
TRENDING_URL = "https://query2.finance.yahoo.com/v1/finance/trending/US"

def fetch_news_catalysts(limit: int = 20):
    results = []

    # Step 1: Get trending tickers from Yahoo
    try:
        resp = requests.get(TRENDING_URL, headers=HEADERS, timeout=10)
        data = resp.json()
        symbols = [q["symbol"] for q in data["finance"]["result"][0]["quotes"][:50]]
    except Exception as e:
        print("ERROR fetching trending tickers:", e)
        return []

    # Step 2: Fetch news for each symbol
    for sym in symbols:
        try:
            url = SEARCH_URL.format(symbol=sym)
            resp = requests.get(url, headers=HEADERS, timeout=10)
            data = resp.json()

            items = data.get("news", [])
            if not items:
                continue

            for item in items[:3]:  # limit per symbol
                title = item.get("title")
                publisher = item.get("publisher")
                link = item.get("link")

                if not title:
                    continue

                results.append({
                    "symbol": sym,
                    "headline": title,
                    "publisher": publisher,
                    "link": link
                })

        except Exception as e:
            print("ERROR fetching news for", sym, ":", e)
            continue

    # Step 3: Deduplicate by symbol
    seen = set()
    unique = []

    for r in results:
        if r["symbol"] not in seen:
            seen.add(r["symbol"])
            unique.append(r)

    return unique[:limit]
