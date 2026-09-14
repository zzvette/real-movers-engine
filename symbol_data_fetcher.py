# symbol_data_fetcher.py

import requests

HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch_symbol_data(symbol: str):
    """
    Fetch live price, change, change_pct, volume for a ticker
    using Yahoo Finance's public quote endpoint.
    """
    url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}"

    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        data = resp.json()
        quote = data["quoteResponse"]["result"][0]
    except Exception:
        return None

    try:
        price = float(quote.get("regularMarketPrice", 0.0))
        change = float(quote.get("regularMarketChange", 0.0))
        change_pct = float(quote.get("regularMarketChangePercent", 0.0))
        volume = int(quote.get("regularMarketVolume", 0))
    except Exception:
        return None

    return {
        "symbol": symbol,
        "price": price,
        "change": change,
        "change_pct": change_pct,
        "volume": volume,
    }
