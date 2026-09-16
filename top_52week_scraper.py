from playwright.sync_api import sync_playwright

FINVIZ_URL = "https://finviz.com/screener.ashx?v=111&s=ta_newhigh"

def fetch_52week_gainers(limit=10):
    results = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(FINVIZ_URL, timeout=60000)
            page.wait_for_selector("table.screener-table", timeout=60000)

            rows = page.locator("table.screener-table tr").all()[1:]  # skip header

            if not rows:
                print("DEBUG: No rows found — Finviz layout may have changed.")
                return []

            for row in rows[:limit]:
                cols = row.locator("td").all()

                # Updated column indexes for v=111
                symbol = cols[1].inner_text().strip()
                price = float(cols[2].inner_text().replace(",", ""))
                change_pct = float(cols[5].inner_text().replace("%", "").replace("+", "").replace(",", ""))
                volume = int(cols[7].inner_text().replace(",", ""))

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

    except Exception as e:
        print("ERROR in fetch_52week_gainers:", e)
        return []

    return results
