import yfinance as yf

# A static universe of liquid, high-volume stocks
UNIVERSE = [
    "AAPL", "MSFT", "NVDA", "TSLA", "AMZN",
    "META", "GOOGL", "AMD", "NFLX", "INTC",
    "CRM", "AVGO", "QCOM", "CSCO", "ORCL",
]

def fetch_top_gainers(limit=10):
    results = []

    for sym in UNIVERSE:
        try:
            t = yf.Ticker(sym)
            info = t.info

            price = info.get("currentPrice")
            change_pct = info.get("regularMarketChangePercent")
            volume = info.get("regularMarketVolume")

            if price is None or change_pct is None:
                continue

            results.append({
                "symbol": sym,
                "price": price,
                "change_pct": change_pct,
                "volume": volume
            })

        except Exception:
            continue

    # Sort by percent change descending
    results.sort(key=lambda x: x["change_pct"], reverse=True)

    return results[:limit]


if __name__ == "__main__":
    gainers = fetch_top_gainers(limit=10)

    print("\n=== LOCAL TOP GAINERS (yfinance) ===")
    for g in gainers:
        print(g)
