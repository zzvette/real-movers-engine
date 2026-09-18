import requests
import yfinance as yf

TRENDING_URL = "https://query2.finance.yahoo.com/v1/finance/trending/US"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def fetch_trending_symbols(limit=25):
    try:
        resp = requests.get(TRENDING_URL, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        quotes = data["finance"]["result"][0]["quotes"]
        return [q["symbol"] for q in quotes[:limit]]
    except Exception as e:
        print("Error fetching trending symbols:", e)
        return []

def fetch_quotes(symbols):
    results = []

    for sym in symbols:
        try:
            t = yf.Ticker(sym)
            info = t.info

            price = info.get("currentPrice")
            change_pct = info.get("regularMarketChangePercent")
            volume = info.get("regularMarketVolume")

            results.append({
                "symbol": sym,
                "price": price,
                "change_pct": change_pct,
                "volume": volume
            })
        except Exception:
            continue

    return results


if __name__ == "__main__":
    symbols = fetch_trending_symbols(limit=25)

    print("\n=== TRENDING SYMBOLS ===")
    print(symbols)

    data = fetch_quotes(symbols)

    print("\n=== TRENDING STOCKS WITH QUOTES ===")
    for item in data:
        print(item)
