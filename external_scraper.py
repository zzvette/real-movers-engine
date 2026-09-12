# external_scraper.py

import time
import requests
from typing import List, Dict, Any, Tuple
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}


# -----------------------------
# Core HTTP helper
# -----------------------------
def _get_html(url: str, params: Dict[str, Any] | None = None) -> BeautifulSoup | None:
    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return None
        return BeautifulSoup(resp.text, "html.parser")
    except Exception:
        return None


# -----------------------------
# FINVIZ SCRAPERS
# -----------------------------
def scrape_finviz_gainers() -> List[Dict[str, Any]]:
    url = "https://finviz.com/screener.ashx"
    params = {"v": "111", "s": "ta_topgainers"}
    soup = _get_html(url, params)
    if soup is None:
        return []

    data = []
    table = soup.find("table", class_="table-light")
    if not table:
        return data

    rows = table.find_all("tr")[1:]  # skip header
    for row in rows:
        cols = [c.get_text(strip=True) for c in row.find_all("td")]
        if len(cols) < 10:
            continue
        symbol = cols[1]
        price = _safe_float(cols[8])
        change_pct = _parse_change_pct(cols[9])
        volume = _safe_int(cols[10])
        data.append(
            {
                "source": "finviz_gainers",
                "symbol": symbol,
                "price": price,
                "change_pct": change_pct,
                "volume": volume,
            }
        )
    return data


def scrape_finviz_losers() -> List[Dict[str, Any]]:
    url = "https://finviz.com/screener.ashx"
    params = {"v": "111", "s": "ta_toplosers"}
    soup = _get_html(url, params)
    if soup is None:
        return []

    data = []
    table = soup.find("table", class_="table-light")
    if not table:
        return data

    rows = table.find_all("tr")[1:]
    for row in rows:
        cols = [c.get_text(strip=True) for c in row.find_all("td")]
        if len(cols) < 10:
            continue
        symbol = cols[1]
        price = _safe_float(cols[8])
        change_pct = _parse_change_pct(cols[9])
        volume = _safe_int(cols[10])
        data.append(
            {
                "source": "finviz_losers",
                "symbol": symbol,
                "price": price,
                "change_pct": change_pct,
                "volume": volume,
            }
        )
    return data


def scrape_finviz_unusual_volume() -> List[Dict[str, Any]]:
    url = "https://finviz.com/screener.ashx"
    params = {"v": "111", "s": "ta_unusualvolume"}
    soup = _get_html(url, params)
    if soup is None:
        return []

    data = []
    table = soup.find("table", class_="table-light")
    if not table:
        return data

    rows = table.find_all("tr")[1:]
    for row in rows:
        cols = [c.get_text(strip=True) for c in row.find_all("td")]
        if len(cols) < 10:
            continue
        symbol = cols[1]
        price = _safe_float(cols[8])
        change_pct = _parse_change_pct(cols[9])
        volume = _safe_int(cols[10])
        data.append(
            {
                "source": "finviz_unusual_volume",
                "symbol": symbol,
                "price": price,
                "change_pct": change_pct,
                "volume": volume,
            }
        )
    return data


# -----------------------------
# YAHOO FINANCE SCRAPER (per symbol)
# -----------------------------
def scrape_yahoo_quote(symbol: str) -> Dict[str, Any]:
    url = f"https://finance.yahoo.com/quote/{symbol}"
    soup = _get_html(url)
    if soup is None:
        return {}

    data: Dict[str, Any] = {"symbol": symbol, "source": "yahoo_quote"}

    # Price
    price_span = soup.find("fin-streamer", {"data-field": "regularMarketPrice"})
    if price_span:
        data["price"] = _safe_float(price_span.get_text(strip=True))

    # Change / change %
    change_span = soup.find("fin-streamer", {"data-field": "regularMarketChange"})
    pct_span = soup.find("fin-streamer", {"data-field": "regularMarketChangePercent"})
    if change_span:
        data["change"] = _safe_float(change_span.get_text(strip=True))
    if pct_span:
        data["change_pct"] = _parse_change_pct(pct_span.get_text(strip=True))

    # Volume
    summary_table = soup.find("div", {"id": "quote-summary"})
    if summary_table:
        rows = summary_table.find_all("tr")
        for row in rows:
            label = row.find("td", class_="C($primaryColor)").get_text(strip=True)
            value = row.find("td", class_="Ta(end)").get_text(strip=True)
            if label.lower() == "volume":
                data["volume"] = _safe_int(value.replace(",", ""))

    return data


# -----------------------------
# NASDAQ / NYSE / MARKETWATCH (placeholders)
# -----------------------------
def scrape_nasdaq_most_active() -> List[Dict[str, Any]]:
    # Placeholder: implement HTML parsing for NASDAQ most active page
    # Return list of dicts with symbol, price, change_pct, volume, source="nasdaq_active"
    return []


def scrape_nyse_most_active() -> List[Dict[str, Any]]:
    # Placeholder: implement HTML parsing for NYSE most active page
    return []


def scrape_marketwatch_movers() -> List[Dict[str, Any]]:
    # Placeholder: implement HTML parsing for MarketWatch gainers/losers/most active
    return []


# -----------------------------
# NEWS / CATALYST SCRAPERS
# -----------------------------
def scrape_finviz_news(symbol: str) -> List[Dict[str, Any]]:
    url = f"https://finviz.com/quote.ashx?t={symbol}"
    soup = _get_html(url)
    if soup is None:
        return []

    news_table = soup.find("table", class_="fullview-news-outer")
    if not news_table:
        return []

    catalysts = []
    rows = news_table.find_all("tr")
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 2:
            continue
        ts = cols[0].get_text(strip=True)
        headline = cols[1].get_text(strip=True)
        source = cols[1].find("span")
        src = source.get_text(strip=True) if source else "Finviz"

        catalysts.append(
            {
                "symbol": symbol,
                "headline": headline,
                "timestamp_raw": ts,
                "source": src,
                "origin": "finviz_news",
            }
        )
    return catalysts


def scrape_yahoo_news(symbol: str) -> List[Dict[str, Any]]:
    url = f"https://finance.yahoo.com/quote/{symbol}/news"
    soup = _get_html(url)
    if soup is None:
        return []

    items = soup.find_all("li", {"class": "js-stream-content"})
    catalysts = []
    for item in items:
        h = item.find("h3")
        if not h:
            continue
        headline = h.get_text(strip=True)
        src_span = item.find("span", {"class": "C(#959595)"})
        src = src_span.get_text(strip=True) if src_span else "Yahoo Finance"

        catalysts.append(
            {
                "symbol": symbol,
                "headline": headline,
                "source": src,
                "origin": "yahoo_news",
            }
        )
    return catalysts


def scrape_marketwatch_news(symbol: str) -> List[Dict[str, Any]]:
    # Placeholder: implement MarketWatch company news scraping
    return []


# -----------------------------
# CATALYST COMBINER
# -----------------------------
def collect_catalysts_for_symbol(symbol: str) -> List[Dict[str, Any]]:
    catalysts: List[Dict[str, Any]] = []

    catalysts.extend(scrape_finviz_news(symbol))
    time.sleep(0.5)
    catalysts.extend(scrape_yahoo_news(symbol))
    time.sleep(0.5)
    catalysts.extend(scrape_marketwatch_news(symbol))

    return catalysts


# -----------------------------
# MASTER EXTERNAL SCREENER ENTRY POINT
# -----------------------------
def get_external_screener_data() -> Tuple[List[Dict[str, Any]], Dict[str, List[Dict[str, Any]]]]:
    """
    Returns:
        all_rows: list of raw symbol dicts from all sources
        catalysts_by_symbol: {symbol: [catalyst_dict, ...]}
    """
    all_rows: List[Dict[str, Any]] = []

    # Finviz
    all_rows.extend(scrape_finviz_gainers())
    time.sleep(0.5)
    all_rows.extend(scrape_finviz_losers())
    time.sleep(0.5)
    all_rows.extend(scrape_finviz_unusual_volume())

    # NASDAQ / NYSE / MarketWatch (when implemented)
    all_rows.extend(scrape_nasdaq_most_active())
    all_rows.extend(scrape_nyse_most_active())
    all_rows.extend(scrape_marketwatch_movers())

    # Deduplicate by symbol + source
    dedup: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for row in all_rows:
        key = (row.get("symbol", ""), row.get("source", ""))
        dedup[key] = row
    all_rows = list(dedup.values())

    # Collect catalysts per symbol
    catalysts_by_symbol: Dict[str, List[Dict[str, Any]]] = {}
    for row in all_rows:
        symbol = row["symbol"]
        cats = collect_catalysts_for_symbol(symbol)
        if cats:
            catalysts_by_symbol[symbol] = cats

    return all_rows, catalysts_by_symbol


# -----------------------------
# Small helpers
# -----------------------------
def _safe_float(s: str) -> float | None:
    try:
        return float(s.replace("%", "").replace("+", "").replace(",", ""))
    except Exception:
        return None


def _safe_int(s: str) -> int | None:
    try:
        return int(s.replace(",", ""))
    except Exception:
        return None


def _parse_change_pct(s: str) -> float | None:
    # e.g. "+4.23%" or "-3.10%"
    try:
        return float(s.replace("%", "").replace("+", "").replace(",", ""))
    except Exception:
        return None


if __name__ == "__main__":
    rows, catalysts = get_external_screener_data()
    print(f"Scraped {len(rows)} symbols")
    print(f"Catalysts for {len(catalysts)} symbols")
