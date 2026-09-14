# external_scraper.py

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


# ---------------------------------------------------------
# EXISTING SCRAPERS (example stubs)
# ---------------------------------------------------------
def scrape_finviz_gainers() -> List[Dict[str, Any]]:
    # Your existing Finviz scraping logic here
    # Return list of dicts: {symbol, price, change_pct, volume}
    return []


def scrape_finviz_losers() -> List[Dict[str, Any]]:
    # Your existing Finviz losers scraping logic here
    return []


# ---------------------------------------------------------
# YAHOO PREMARKET GAINERS
# ---------------------------------------------------------
def scrape_yahoo_premarket() -> List[Dict[str, Any]]:
    """
    Scrape Yahoo Finance pre-market gainers.
    URL is updated to pull up to 100 symbols.
    """
    url = "https://finance.yahoo.com/markets/stocks/gainers?count=100&offset=0"
    resp = requests.get(url, headers=HEADERS, timeout=10)
    if resp.status_code != 200:
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    table = soup.find("table")
    if not table:
        return []

    rows = table.find_all("tr")
    results: List[Dict[str, Any]] = []

    for row in rows[1:]:
        cols = row.find_all("td")
        if len(cols) < 6:
            continue

        try:
            symbol = cols[0].get_text(strip=True)
            price = float(cols[2].get_text(strip=True).replace(",", ""))
            change_str = cols[3].get_text(strip=True)
            change_pct_str = cols[4].get_text(strip=True)
            volume_str = cols[5].get_text(strip=True).replace(",", "")

            # Parse change and change_pct
            change = float(change_str.replace("+", "").replace("%", ""))
            change_pct = float(change_pct_str.replace("+", "").replace("%", ""))
            volume = int(volume_str)
        except Exception:
            continue

        results.append(
            {
                "symbol": symbol,
                "price": price,
                "change": change,
                "change_pct": change_pct,
                "volume": volume,
            }
        )

    return results
