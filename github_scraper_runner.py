import json
from datetime import datetime, timezone

from top_gainers_scraper import fetch_top_gainers
from top_52week_scraper import fetch_52week_gainers
from news_scraper import fetch_news_catalysts


def save_json(path: str, payload: dict):
    with open(path, "w") as f:
        json.dump(payload, f, indent=4)


def debug_print(name, data):
    print(f"\n===== DEBUG: {name} =====")
    print(f"Type: {type(data)}")
    print(f"Length: {len(data) if hasattr(data, '__len__') else 'N/A'}")
    print("Sample:", data[:3] if isinstance(data, list) else data)
    print("=========================\n")


def run_all_scrapers():
    # FIXED: GitHub Actions Python 3.10 does NOT support UTC import
    timestamp = datetime.now(timezone.utc).isoformat()

    # ---------------------------------------------------------
    # RUN SCRAPERS
    # ---------------------------------------------------------
    gainers = fetch_top_gainers(limit=10)
    highs = fetch_52week_gainers(limit=10)
    catalysts = fetch_news_catalysts(limit=20)

    # ---------------------------------------------------------
    # DEBUG OUTPUT
    # ---------------------------------------------------------
    debug_print("TOP GAINERS RAW", gainers)
    debug_print("52-WEEK HIGHS RAW", highs)
    debug_print("NEWS CATALYSTS RAW", catalysts)

    # ---------------------------------------------------------
    # BUILD DAILY SCREENER
    # ---------------------------------------------------------
    daily_screener = {
        "timestamp": timestamp,
        "signals": {
            "gainers": gainers,
            "highs": highs,
            "catalysts": catalysts,
        },
    }

    # ---------------------------------------------------------
    # SAVE JSON OUTPUTS
    # ---------------------------------------------------------
    save_json("top_gainers.json", {"timestamp": timestamp, "top_gainers": gainers})
    save_json("top_52week.json", {"timestamp": timestamp, "top_52week": highs})
    save_json("catalyst_log.json", {"timestamp": timestamp, "catalysts": daily_screener["signals"]["catalysts"]})
    save_json("daily_screener.json", daily_screener)

    # ---------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------
    print("Scraper run complete.")
    print(f"Gainers: {len(gainers)} | Highs: {len(highs)} | Catalysts: {len(catalysts)}")


if __name__ == "__main__":
    run_all_scrapers()
