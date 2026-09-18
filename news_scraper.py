import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

SEARCH_URL = "https://query2.finance.yahoo.com/v1/finance/search?q={symbol}"
TRENDING_URL = "https://query2.finance.yahoo.com/v1/finance/trending/US"

# ---------------------------------------------------------
# KEYWORD GROUPS (your updated ranking)
# ---------------------------------------------------------

# Highest priority: movement words
MOVEMENT_WORDS = [
    "raised", "climbs", "climbed", "gainers", "gaining", "moving",
    "jumps", "jumped", "surges", "surged", "spikes", "spiked",
    "rebounds", "breakout", "breaks out"
]

# Second priority: money / institutional words
MONEY_WORDS = [
    "dollars", "cash", "percentage", "percent", "merger", "acquisition",
    "financing", "offering", "agreement", "deal", "valuation", "buyout"
]

# ---------------------------------------------------------
# SCORING FUNCTION
# ---------------------------------------------------------

def score_headline(text):
    """Score a headline based on movement and money keywords."""
    text_lower = text.lower()
    score = 0

    # Movement words = +3 each (highest priority)
    for w in MOVEMENT_WORDS:
        if w in text_lower:
            score += 3

    # Money words = +2 each (second priority)
    for w in MONEY_WORDS:
        if w in text_lower:
            score += 2

    return score


# ---------------------------------------------------------
# MAIN SCRAPER
# ---------------------------------------------------------

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

                # Score the headline
                score = score_headline(title)

                results.append({
                    "symbol": sym,
                    "headline": title,
                    "publisher": publisher,
                    "link": link,
                    "score": score
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

    # Step 4: Sort by score (highest first)
    unique_sorted = sorted(unique, key=lambda x: x["score"], reverse=True)

    return unique_sorted[:limit]
