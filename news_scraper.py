# news_scraper.py

import requests
from bs4 import BeautifulSoup
import re

HEADERS = {"User-Agent": "Mozilla/5.0"}

# ---------------------------------------------------------
# Utility: Extract tickers from headline text
# ---------------------------------------------------------
def extract_symbols_from_text(text: str):
    # crude but effective: tickers are 1–5 uppercase letters
    candidates = re.findall(r"\b[A-Z]{1,5}\b", text)
    # filter out common non‑tickers
    blacklist = {"CEO", "EPS", "FDA", "SEC", "Q1", "Q2", "Q3", "Q4"}
    return [c for c in candidates if c not in blacklist]


# ---------------------------------------------------------
# MarketWatch Latest Business News
# ---------------------------------------------------------
def scrape_marketwatch_news():
    url = "https://www.marketwatch.com/latest-news"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
    except Exception:
        return []

    results = []
    articles = soup.select("div.article__content")

    for a in articles:
        headline = a.get_text(strip=True)
        symbols = extract_symbols_from_text(headline)
        if symbols:
            results.append({
                "source": "MarketWatch",
                "headline": headline,
                "symbols": symbols
            })

    return results


# ---------------------------------------------------------
# Yahoo Finance Latest News
# ---------------------------------------------------------
def scrape_yahoo_news():
    url = "https://finance.yahoo.com/topic/latest-news"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
    except Exception:
        return []

    results = []
    items = soup.select("h3")

    for item in items:
        headline = item.get_text(strip=True)
        symbols = extract_symbols_from_text(headline)
        if symbols:
            results.append({
                "source": "Yahoo Finance",
                "headline": headline,
                "symbols": symbols
            })

    return results


# ---------------------------------------------------------
# Benzinga Breaking News
# ---------------------------------------------------------
def scrape_benzinga_news():
    url = "https://www.benzinga.com/news"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
    except Exception:
        return []

    results = []
    items = soup.select("a.title")

    for item in items:
        headline = item.get_text(strip=True)
        symbols = extract_symbols_from_text(headline)
        if symbols:
            results.append({
                "source": "Benzinga",
                "headline": headline,
                "symbols": symbols
            })

    return results


# ---------------------------------------------------------
# NASDAQ Earnings Calendar
# ---------------------------------------------------------
def scrape_nasdaq_earnings():
    url = "https://www.nasdaq.com/market-activity/earnings"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
    except Exception:
        return []

    results = []
    rows = soup.select("tbody tr")

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 2:
            continue

        symbol = cols[0].get_text(strip=True)
        headline = f"Earnings event for {symbol}"
        results.append({
            "source": "NASDAQ Earnings",
            "headline": headline,
            "symbols": [symbol]
        })

    return results


# ---------------------------------------------------------
# SEC 8‑K Filings (corporate events)
# ---------------------------------------------------------
def scrape_sec_8k():
    url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
    except Exception:
        return []

    results = []
    rows = soup.select("tr")

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 4:
            continue

        form_type = cols[0].get_text(strip=True)
        if form_type != "8-K":
            continue

        company = cols[1].get_text(strip=True)
        headline = f"SEC 8-K filing: {company}"
        symbols = extract_symbols_from_text(company)

        if symbols:
            results.append({
                "source": "SEC 8-K",
                "headline": headline,
                "symbols": symbols
            })

    return results


# ---------------------------------------------------------
# MASTER: Pull all catalyst sources (N4)
# ---------------------------------------------------------
def scrape_all_news_sources():
    results = []
    results.extend(scrape_marketwatch_news())
    results.extend(scrape_yahoo_news())
    results.extend(scrape_benzinga_news())
    results.extend(scrape_nasdaq_earnings())
    results.extend(scrape_sec_8k())
    return results
