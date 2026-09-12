# github_scraper_runner.py

import json
import datetime

from combined_screener import build_combined_screener


def save_json(path: str, data: dict):
    """
    Save JSON to the repo so GitHub Actions can commit it.
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def main():
    print("Running external scrapers and building combined screener...")

    # Build everything from external scrapers
    raw_by_day, real_movers, catalyst_log = build_combined_screener()

    # Prepare JSON structures for GitHub
    daily_screener_json = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "raw_by_day": raw_by_day
    }

    real_movers_json = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "real_movers": real_movers
    }

    catalyst_log_json = catalyst_log  # already structured

    # Save files to repo root
    save_json("daily_screener.json", daily_screener_json)
    save_json("real_movers.json", real_movers_json)
    save_json("catalyst_log.json", catalyst_log_json)

    print("JSON files generated:")
    print(" - daily_screener.json")
    print(" - real_movers.json")
    print(" - catalyst_log.json")
    print("Done.")


if __name__ == "__main__":
    main()
