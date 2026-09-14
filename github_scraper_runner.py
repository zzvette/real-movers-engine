# github_scraper_runner.py

import json
import datetime

from top_gainers_scraper import fetch_top_gainers
from top_52week_scraper import fetch_52week_gainers
from news_scraper import scrape_all_news_sources
from combined_screener import score_entry_for_symbol


def main():
    timestamp = datetime.datetime.utcnow().isoformat()

    # ---------------------------------------------------------
    # 1. Fetch gainers
    # ---------------------------------------------------------
    top_gainers = fetch_top_gainers(limit=5)
    top_52week = fetch_52week_gainers(limit=5)

    # ---------------------------------------------------------
    # 2. Fetch catalysts (news)
    # ---------------------------------------------------------
    news_items = scrape_all_news_sources()

    catalyst_log = {"catalysts": {}}

    # Map catalysts to symbols
    for item in news_items:
        for sym in item["symbols"]:
            catalyst_log["catalysts"].setdefault(sym, []).append({
                "source": item["source"],
                "headline": item["headline"]
            })

    # ---------------------------------------------------------
    # 3. Score gainers using your strict scoring engine
    # ---------------------------------------------------------
    for entry in top_gainers:
        sym = entry["symbol"]
        catalysts = catalyst_log["catalysts"].get(sym, [])
        entry["score"] = score_entry_for_symbol(entry, catalysts)

    for entry in top_52week:
        sym = entry["symbol"]
        catalysts = catalyst_log["catalysts"].get(sym, [])
        entry["score"] = score_entry_for_symbol(entry, catalysts)

    # ---------------------------------------------------------
    # 4. Write JSON files for Streamlit
    # ---------------------------------------------------------
    with open("top_gainers.json", "w") as f:
        json.dump({
            "timestamp": timestamp,
            "top_gainers": top_gainers
        }, f, indent=4)

    with open("top_52week.json", "w") as f:
        json.dump({
            "timestamp": timestamp,
            "top_52week": top_52week
        }, f, indent=4)

    with open("catalyst_log.json", "w") as f:
        json.dump({
            "timestamp": timestamp,
            "catalysts": catalyst_log["catalysts"]
        }, f, indent=4)

    # Daily screener placeholder (calendar)
    with open("daily_screener.json", "w") as f:
        json.dump({
            "timestamp": timestamp,
            "raw_by_day": {}
        }, f, indent=4)


if __name__ == "__main__":
    main()
