import json
from datetime import datetime, timezone

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
    """Run catalyst-only scraper and produce JSON outputs."""

    timestamp = datetime.now(timezone.utc).isoformat()

    # ---------------------------------------------------------
    # RUN SCRAPER (Catalyst Only)
    # ---------------------------------------------------------
    try:
        catalysts = fetch_news_catalysts(limit=50)
    except Exception as e:
        print("ERROR in fetch_news_catalysts:", e)
        catalysts = []

    # ---------------------------------------------------------
    # DEBUG OUTPUT
    # ---------------------------------------------------------
    debug_print("NEWS CATALYSTS RAW", catalysts)

    # ---------------------------------------------------------
    # BUILD DAILY SCREENER
    # ---------------------------------------------------------
    daily_screener = {
        "timestamp": timestamp,
        "signals": {
            "catalysts": catalysts,
        },
    }

    # ---------------------------------------------------------
    # SAVE JSON OUTPUTS
    # ---------------------------------------------------------
    save_json("catalyst_log.json", {
        "timestamp": timestamp,
        "catalysts": catalysts
    })

    save_json("daily_screener.json", daily_screener)

    # ---------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------
    print("Scraper run complete.")
    print(f"Catalysts: {len(catalysts)}")


if __name__ == "__main__":
    run_all_scrapers()
