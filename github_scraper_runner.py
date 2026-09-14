# github_scraper_runner.py

import json
import datetime
from combined_screener import build_combined_screener


def main():
    result = build_combined_screener()
    timestamp = datetime.datetime.utcnow().isoformat()

    # Write top gainers
    with open("top_gainers.json", "w") as f:
        json.dump({
            "timestamp": timestamp,
            "top_gainers": result["top_gainers"]
        }, f, indent=4)

    # Write 52-week gainers
    with open("top_52week.json", "w") as f:
        json.dump({
            "timestamp": timestamp,
            "top_52week": result["top_52week"]
        }, f, indent=4)

    # Write catalyst log
    with open("catalyst_log.json", "w") as f:
        json.dump({
            "timestamp": timestamp,
            "catalysts": result["catalyst_log"]["catalysts"]
        }, f, indent=4)


if __name__ == "__main__":
    main()
