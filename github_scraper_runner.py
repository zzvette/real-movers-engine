import json
from datetime import datetime, timezone

# Correct imports — these MUST be functions, not modules
from top_gainers_scraper import fetch_top_gainers
from top_52week_scraper import fetch_52week_gainers
from news_scraper import fetch_news_catalysts


def save_json(path: str, payload: dict):
    """Write JSON to disk with pretty formatting."""
    with open(path, "w") as f:
        json.dump(payload, f, indent=4)


def debug_print(name: str, data):
    """Print structured debug output for GitHub Actions logs."""
    print(f"\n===== DEBUG: {name} =====")
    print(f"Type: {type(data)}")

    try:
        length = len(data)
    except Exception:
        length = "N/A"

    print(f"Length: {length}")

    if isinstance(data, list):
        print("Sample:", data[:3])
    else:
        print("Sample:", data)

    print("=========================\n")


def run_all_scrapers():
    """Run all scrapers and produce JSON outputs."""

    # GitHub Actions-safe timestamp
    timestamp = datetime.now(timezone.utc).isoformat()

    # ---------------------------------------------------------
    # RUN SCRAPERS
    # ---------------------------------------------------------
    try:
        gainers = fetch_top_gainers(limit=10)
    except Exception as e:
        print("ERROR in fetch_top_gainers:", e)
        gainers = []

    try:
        highs = fetch_52week_gainers(limit=10)
    except Exception as e:
        print("ERROR in fetch_52week_gainers:", e)
        highs = []

    try:
        catalysts = fetch_news_catalysts(limit=20)
    except Exception as e:
        print("ERROR in fetch_news_catalysts:", e)
        catalysts = []

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
    save_json("top_gainers.json", {
        "timestamp": timestamp,
        "top_gainers": gainers
    })

    save_json("top_52week.json", {
        "timestamp": timestamp,
        "top_52week": highs
    })

    save_json("catalyst_log.json", {
        "timestamp": timestamp,
        "catalysts": catalysts
    })

    save_json("daily_screener.json", daily_screener)

    # ---------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------
    print("Scraper run complete.")
    print(f"Gainers: {len(gainers)} | Highs: {len(highs)} | Catalysts: {len(catalysts)}")


if __name__ == "__main__":
    run_all_scrapers()
