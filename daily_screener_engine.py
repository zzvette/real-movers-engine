import requests
import yfinance as yf
import json
from datetime import datetime, UTC

TRENDING_URL = "https://query2.finance.yahoo.com/v1/finance/trending/US"
NEWS_URL = "https://query2.finance.yahoo.com/v1/finance/search?q={symbol}"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

# ---------------------------------------------------------
# TRENDING SYMBOLS
# ---------------------------------------------------------
def fetch_trending_symbols(limit=25):
    try:
        resp = requests.get(TRENDING_URL, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        quotes = data["finance"]["result"][0]["quotes"]
        return [q["symbol"] for q in quotes[:limit]]
    except Exception:
        return []

# ---------------------------------------------------------
# QUOTES
# ---------------------------------------------------------
def fetch_quotes(symbols):
    results = []

    for sym in symbols:
        try:
            t = yf.Ticker(sym)
            info = t.info

            price = info.get("currentPrice")
            change_pct = info.get("regularMarketChangePercent")
            volume = info.get("regularMarketVolume")
            high_52 = info.get("fiftyTwoWeekHigh")
            low_52 = info.get("fiftyTwoWeekLow")

            if price is None:
                continue

            results.append({
                "symbol": sym,
                "price": price,
                "change_pct": change_pct,
                "volume": volume,
                "high_52": high_52,
                "low_52": low_52
            })

        except Exception:
            continue

    return results

# ---------------------------------------------------------
# GAINERS
# ---------------------------------------------------------
def fetch_gainers(quotes, limit=10):
    valid = [q for q in quotes if q["change_pct"] is not None]
    valid.sort(key=lambda x: x["change_pct"], reverse=True)
    return valid[:limit]

# ---------------------------------------------------------
# 52-WEEK HIGHS
# ---------------------------------------------------------
def fetch_highs(quotes, limit=10):
    highs = []

    for q in quotes:
        if q["high_52"] is None:
            continue

        dist = q["price"] / q["high_52"]

        if dist >= 0.97:  # near-high band
            highs.append(q)

    highs.sort(key=lambda x: x["change_pct"] or 0, reverse=True)
    return highs[:limit]

# ---------------------------------------------------------
# CATALYSTS
# ---------------------------------------------------------
def fetch_news(symbol):
    try:
        url = NEWS_URL.format(symbol=symbol)
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        items = data.get("news", [])
        catalysts = []

        for item in items:
            title = item.get("title")
            link = item.get("link")
            publisher = item.get("publisher")

            if not title:
                continue

            catalysts.append({
                "title": title,
                "publisher": publisher,
                "link": link
            })

        return catalysts

    except Exception:
        return []

def fetch_catalysts(symbols):
    results = []

    for sym in symbols:
        cats = fetch_news(sym)
        if cats:
            results.append({
                "symbol": sym,
                "catalysts": cats
            })

    return results

# ---------------------------------------------------------
# SAVE JSON
# ---------------------------------------------------------
def save_json(path, payload):
    with open(path, "w") as f:
        json.dump(payload, f, indent=4)

# ---------------------------------------------------------
# MAIN ENGINE
# ---------------------------------------------------------
def run_engine():
    timestamp = datetime.now(UTC).isoformat()

    trending_symbols = fetch_trending_symbols()
    trending_quotes = fetch_quotes(trending_symbols)
    gainers = fetch_gainers(trending_quotes)
    highs = fetch_highs(trending_quotes)
    catalysts = fetch_catalysts(trending_symbols)

    payload = {
        "timestamp": timestamp,
        "signals": {
            "trending": trending_quotes,
            "gainers": gainers,
            "highs": highs,
            "catalysts": catalysts
        }
    }

    save_json("daily_screener.json", payload)

    print("\nEngine complete.")
    print(f"Trending: {len(trending_quotes)}")
    print(f"Gainers: {len(gainers)}")
    print(f"Highs: {len(highs)}")
    print(f"Catalysts: {len(catalysts)}")

if __name__ == "__main__":
    run_engine()
