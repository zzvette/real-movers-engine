# github_scraper_runner.py (yfinance version)

import json
from datetime import datetime, UTC

from top_gainers_scraper import fetch_top_gainers
from top_52week_scraper import fetch_52week_gainers
from news_scraper import fetch_news_catalysts


def save_json(path: str, payload: dict):
    with open(path, "w") as f:
        json.dump(payload, f, indent=4)


def run_all_scrapers():
    timestamp = datetime.now(UTC).isoformat()

    gainers = fetch_top_gainers(limit=10)
    highs = fetch_52week_gainers(limit=10)
    catalysts = fetch_news_catalysts(limit=20)

    daily_screener = {
        "timestamp": timestamp,
        "signals": {
            "gainers": gainers,
            "highs": highs,
            "catalysts": {c["symbol"]: c["headline"] for c in catalysts},
        },
    }

    save_json("top_gainers.json", {"timestamp": timestamp, "top_gainers": gainers})
    save_json("top_52week.json", {"timestamp": timestamp, "top_52week": highs})
    save_json("catalyst_log.json", {"timestamp": timestamp, "catalysts": daily_screener["signals"]["catalysts"]})
    save_json("daily_screener.json", daily_screener)

    print("Scraper run complete.")
    print(f"Gainers: {len(gainers)} | Highs: {len(highs)} | Catalysts: {len(catalysts)}")


if __name__ == "__main__":
    run_all_scrapers()
