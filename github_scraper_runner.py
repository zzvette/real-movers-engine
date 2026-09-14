# github_scraper_runner.py

import json
import datetime

from combined_screener import build_combined_screener


def main():
    # GitHub Action: run in pre-market mode for morning scan
    raw_by_day, real_movers, catalyst_log = build_combined_screener(premarket=True)

    timestamp = datetime.datetime.utcnow().isoformat()

    with open("daily_screener.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "timestamp": timestamp,
                "raw_by_day": raw_by_day,
            },
            f,
            indent=4,
        )

    with open("real_movers.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "timestamp": timestamp,
                "real_movers": real_movers,
            },
            f,
            indent=4,
        )

    with open("catalyst_log.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "timestamp": timestamp,
                "catalysts": catalyst_log.get("catalysts", {}),
            },
            f,
            indent=4,
        )


if __name__ == "__main__":
    main()
