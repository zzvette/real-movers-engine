# combined_screener.py

from top_gainers_scraper import fetch_top_gainers
from top_52week_scraper import fetch_52week_gainers
from news_scraper import scrape_all_news_sources
from reversal_engine import score_signal
import datetime


def build_combined_screener():
    today = datetime.date.today()
    day_num = today.day

    # Pull gainers
    top_gainers = fetch_top_gainers(limit=5)
    top_52week = fetch_52week_gainers(limit=5)

    # Pull catalysts
    news_items = scrape_all_news_sources()

    catalyst_log = {"catalysts": {}}

    # Map catalysts to symbols
    for item in news_items:
        for sym in item["symbols"]:
            catalyst_log["catalysts"].setdefault(sym, []).append({
                "source": item["source"],
                "headline": item["headline"]
            })

    # Score gainers
    def score_entry(entry):
        sym = entry["symbol"]
        catalysts = catalyst_log["catalysts"].get(sym, [])
        return score_signal(
            price=entry["price"],
            change_pct=entry["change_pct"],
            volume=entry["volume"],
            catalysts=catalysts,
            premarket=False
        )

    for entry in top_gainers:
        entry["score"] = score_entry(entry)

    for entry in top_52week:
        entry["score"] = score_entry(entry)

    return {
        "top_gainers": top_gainers,
        "top_52week": top_52week,
        "catalyst_log": catalyst_log,
        "day": day_num
    }
