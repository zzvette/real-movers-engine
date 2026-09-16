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
            "catalysts": catalysts,
        },
    }

    save_json("daily_screener.json", daily_screener)

    print("Scraper run complete.")
    print(f"Gainers: {len(gainers)} | Highs: {len(highs)} | Catalysts: {len(catalysts)}")

if __name__ == "__main__":
    run_all_scrapers()
