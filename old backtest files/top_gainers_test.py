import requests

URL = "https://www.marketwatch.com/tools/screener/gainers"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def fetch_top_gainers(limit=10):
    try:
        resp = requests.get(URL, headers=HEADERS, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print("Request error:", e)
        return []

    # MarketWatch embeds JSON inside the HTML
    text = resp.text

    # Find the JSON block
    start = text.find("var data = ") + len("var data = ")
    end = text.find(";\n", start)

    if start == -1 or end == -1:
        print("Could not locate JSON block.")
        return []

    import json
    try:
        data = json.loads(text[start:end])
    except Exception as e:
        print("JSON parse error:", e)
        return []

    results = []

    for row in data.get("results", [])[:limit]:
        try:
            results.append({
                "symbol": row["symbol"],
                "price": row["last"],
                "change_pct": row["pctChange"],
                "volume": row["volume"]
            })
        except Exception:
            continue

    return results


if __name__ == "__main__":
    gainers = fetch_top_gainers(limit=10)

    print("\n=== TOP GAINERS (MarketWatch) ===")
    for g in gainers:
        print(g)
