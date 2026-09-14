# external_scraper.py

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


# ---------------------------------------------------------
# TRADINGVIEW PRE-MARKET SCANNER (option E: gainers + volume)
# ---------------------------------------------------------
def scrape_tradingview_premarket(limit: int = 100) -> List[Dict[str, Any]]:
    """
    Use TradingView's scanner API to pull pre-market movers.
    Combines gainers + volume leaders via change% and volume.
    """
    url = "https://scanner.tradingview.com/america/scan"

    payload = {
        "filter": [
            {"left": "exchange", "operation": "in_list", "right": ["NYSE", "NASDAQ", "AMEX"]},
            {"left": "type", "operation": "in_list", "right": ["stock"]},
            {"left": "extended_hours", "operation": "equal", "right": True},
        ],
        "symbols": {
            "query": {"types": ["stock"]},
            "tickers": []
        },
        "columns": [
            "symbol",
            "close",
            "change",
            "change_percent",
            "volume",
        ],
        "sort": {
            "sortBy": "change_percent",
            "sortOrder": "desc"
        },
        "range": [0, limit],
    }

    try:
        resp = requests.post(url, json=payload, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return []
        data = resp.json()
    except Exception:
        return []

    results: List[Dict[str, Any]] = []

    for d in data.get("data", []):
        s = d.get("s")  # symbol
        v = d.get("d", [])  # columns

        if len(v) < 5:
            continue

        try:
            symbol = s.split(":")[-1]
            price = float(v[1])
            change = float(v[2])
            change_pct = float(v[3])
            volume = int(v[4])
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


# ---------------------------------------------------------
# OPTIONAL: YAHOO PRE-MARKET (secondary source)
# ---------------------------------------------------------
def scrape_yahoo_premarket(limit: int = 50) -> List[Dict[str, Any]]:
    """
    Secondary pre-market source from Yahoo.
    Used as a backup to TradingView.
    """
    url = "https://finance.yahoo.com/markets/stocks/gainers?count=100&offset=0"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return []
    except Exception:
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

        if len(results) >= limit:
            break

    return results
