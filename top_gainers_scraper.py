# top_gainers_scraper.py (yfinance version)

import yfinance as yf

def fetch_top_gainers(limit: int = 10):
    try:
        data = yf.get_day_gainers()
        if data is None or data.empty:
            return []
    except Exception:
        return []

    results = []

    for _, row in data.head(limit).iterrows():
        try:
            symbol = row["Symbol"]
            price = float(row["Price"])
            change = float(row["Change"])
            change_pct = float(row["% Change"])
            volume = int(row["Volume"])

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

    return results
