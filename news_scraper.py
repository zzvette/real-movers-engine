import requests
from datetime import datetime, timezone
from typing import List, Dict

YAHOO_NEWS_ENDPOINT = "https://query1.finance.yahoo.com/v1/finance/search"

def fetch_news_for_symbol(symbol: str) -> List[Dict]:
    params = {
        "q": symbol,
        "newsCount": 20,
        "quotesCount": 0,
        "listsCount": 0,
        "enableFuzzyQuery": False,
        "quotesQueryId": "tss_match_phrase_query",
        "newsQueryId": "newssearch_rs",
        "enableCb": False,
        "enableNavLinks": False,
    }
    resp = requests.get(YAHOO_NEWS_ENDPOINT, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    news_items = []
    for item in data.get("news", []):
        news_items.append(
            {
                "symbol": symbol,
                "title": item.get("title"),
                "publisher": item.get("publisher"),
                "link": item.get("link"),
                "published_at": item.get("providerPublishTime"),
            }
        )
    return news_items


def fetch_catalysts(symbols: List[str]) -> List[Dict]:
    all_news = []
    for sym in symbols:
        try:
            all_news.extend(fetch_news_for_symbol(sym))
        except Exception as e:
            print(f"[WARN] Failed news fetch for {sym}: {e}")
    now = datetime.now(timezone.utc).isoformat()
    for item in all_news:
        item["scrape_timestamp"] = now
    return all_news
