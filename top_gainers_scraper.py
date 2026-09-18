from playwright.sync_api import sync_playwright
from playwright_stealth import stealth

FINVIZ_URL = "https://finviz.com/screener.ashx?v=111&s=ta_topgainers"


def fetch_top_gainers(limit=10):
    results = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            stealth(page)

            # Load Finviz
            page.goto(FINVIZ_URL, timeout=60000)

            # Correct table selector (Finviz changed their DOM)
            page.wait_for_selector("table.screener-view-table", timeout=60000)

            # Extract rows (skip header)
            rows = page.locator("table.screener-view-table tr").all()[1:]

            for row in rows[:limit]:
                cols = row.locator("td").all()

                # Finviz column layout for v=111:
                # 0 = No.
                # 1 = Ticker
                # 2 = Company
                # 3 = Sector
                # 4 = Industry
                # 5 = Country
                # 6 = Market Cap
                # 7 = Price
                # 8 = Change %
                # 9 = Volume

                symbol = cols[1].inner_text().strip()

                price = float(cols[7].inner_text().replace(",", ""))

                change_pct = float(
                    cols[8].inner_text()
                    .replace("%", "")
                    .replace("+", "")
                    .replace(",", "")
                )

                volume = int(cols[9].inner_text().replace(",", ""))

                # Scoring logic
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
        print("ERROR in fetch_top_gainers:", e)
        return []

    return results
