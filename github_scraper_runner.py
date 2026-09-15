# github_scraper_runner.py (2026 FIXED)

import json
from datetime import datetime

from top_gainers_scraper import fetch_top_gainers
from top_52week_scraper import fetch_52week_gainers
from news_scraper import fetch_news_catalysts


def save_json(path: str, payload: dict):
    """Write JSON with pretty formatting."""
    with open(path, "w") as f:
        json.dump(payload, f, indent=4)


def run_all_scrapers():
    timestamp = datetime.utcnow().isoformat()

    # --- Fetch data ---
    gainers = fetch_top_gainers(limit=10)
    highs = fetch_52week_gainers(limit=10)
    catalysts = fetch_news_catalysts(limit=20)

    # --- Build JSON outputs ---
    gainers_json = {
        "timestamp": timestamp,
        "top_gainers": gainers,
    }

    highs_json = {
        "timestamp": timestamp,
        "top_52week": highs,
    }

    catalysts_json = {
        "timestamp": timestamp,
        "catalysts": {c["symbol"]: c["headline"] for c in catalysts},
    }

    # --- Combined daily screener ---
    daily_screener = {
        "timestamp": timestamp,
        "signals": {
            "gainers": gainers,
            "highs": highs,
            "catalysts": catalysts_json["catalysts"],
        },
    }

    # --- Save files ---
    save_json("top_gainers.json", gainers_json)
    save_json("top_52week.json", highs_json)
    save_json("catalyst_log.json", catalysts_json)
    save_json("daily_screener.json", daily_screener)

    print("Scraper run complete.")
    print(f"Gainers: {len(gainers)} | Highs: {len(highs)} | Catalysts: {len(catalysts)}")


if __name__ == "__main__":
    run_all_scrapers()
