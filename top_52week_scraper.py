from playwright.sync_api import sync_playwright

FINVIZ_URL = "https://finviz.com/screener.ashx?v=111&s=ta_newhigh"

def fetch_52week_gainers(limit=10):
    results = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(FINVIZ_URL, timeout=60000)

            rows = page.locator("table.table-light tr").all()[1:]  # skip header

            for row in rows[:limit]:
                cols = row.locator("td").all()

                symbol = cols[1].inner_text().strip()
                price = float(cols[8].inner_text().replace(",", ""))
                change_pct = float(cols[9].inner_text().replace("%", "").replace("+", "").replace(",", ""))
                volume = int(cols[10].inner_text().replace(",", ""))

                pct_component = max(min(change_pct * 2, 60), -20)
                vol_component = min(volume / 1_000_000, 40)
                score = int(max(min(pct_component + vol_component, 100), 0))

                results.append({
                    "symbol": symbol,
                    "price": price,
                    "change_pct": change_pct,
                    "volume": volume,
                    "score": score,
                })

            browser.close()

    except Exception:
        return []

    return results
