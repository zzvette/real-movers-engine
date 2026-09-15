# top_52week_scraper.py (yfinance version)

import yfinance as yf

def fetch_52week_gainers(limit: int = 10):
    try:
        data = yf.get_day_gainers()
        if data is None or data.empty:
            return []
    except Exception:
        return []

    results = []

    for _, row in data.iterrows():
        try:
            symbol = row["Symbol"]
            ticker = yf.Ticker(symbol)
            info = ticker.info

            price = info.get("currentPrice")
            high = info.get("fiftyTwoWeekHigh")
            change_pct = info.get("regularMarketChangePercent")
            volume = info.get("regularMarketVolume")

            if not price or not high:
                continue

            if price >= 0.95 * high:
                pct_component = max(min(change_pct * 2, 60), -20)
                vol_component = min((volume or 0) / 1_000_000, 40)
                score = int(max(min(pct_component + vol_component, 100), 0))

                results.append(
                    {
                        "symbol": symbol,
                        "price": price,
                        "change_pct": change_pct,
                        "volume": volume,
                        "score": score,
                    }
                )
        except Exception:
            continue

    results.sort(key=lambda x: x["change_pct"] or 0, reverse=True)
    return results[:limit]
