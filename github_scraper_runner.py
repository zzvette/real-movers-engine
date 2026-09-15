# github_scraper_runner.py

import json
from datetime import datetime

from top_gainers_scraper import fetch_top_gainers
from top_52week_scraper import fetch_52week_gainers
from news_scraper import fetch_news_catalysts


# ----------------------------
# WRITE JSON HELPERS
# ----------------------------
def write_json(path: str, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


# ----------------------------
# MAIN RUNNER
# ----------------------------
def run_all_scrapers():
    timestamp = datetime.utcnow().isoformat()

    # ----------------------------
    # 1. TOP GAINERS
    # ----------------------------
    gainers = fetch_top_gainers()
    top_gainers_payload = {
        "timestamp": timestamp,
        "top_gainers": gainers
    }
    write_json("top_gainers.json", top_gainers_payload)

    # ----------------------------
    # 2. 52-WEEK GAINERS
    # ----------------------------
    highs = fetch_52week_gainers()
    top_52week_payload = {
        "timestamp": timestamp,
        "top_52week": highs
    }
    write_json("top_52week.json", top_52week_payload)

    # ----------------------------
    # 3. NEWS CATALYSTS
    # ----------------------------
    catalysts = fetch_news_catalysts()
    catalyst_payload = {
        "timestamp": timestamp,
        "catalysts": catalysts
    }
    write_json("catalyst_log.json", catalyst_payload)

    # ----------------------------
    # 4. DAILY SCREENER (COMBINED)
    # ----------------------------
    # This file is consumed by Streamlit via data_loader.py
    # Format:
    # [
    #   {
    #       "date": "2026-09-14",
    #       "symbol": "NVDA",
    #       "price": 123.45,
    #       "change": 8.23,
    #       "change_pct": 7.12,
    #       "volume": 45678900,
    #       "score": 82,
    #       "news_catalyst": "Earnings Beat"
    #   },
    #   ...
    # ]

    combined_rows = []

    today_str = datetime.utcnow().strftime("%Y-%m-%d")

    # Merge gainers + 52-week + catalysts into unified rows
    # -----------------------------------------------------

    # 1. Add gainers
    for g in gainers:
        combined_rows.append({
            "date": today_str,
            "symbol": g["symbol"],
            "price": g["price"],
            "change": g["change"],
            "change_pct": g["change_pct"],
            "volume": g["volume"],
            "score": g.get("score", 0),
            "news_catalyst": None
        })

    # 2. Add 52-week highs (avoid duplicates)
    existing_symbols = {row["symbol"] for row in combined_rows}

    for h in highs:
        if h["symbol"] not in existing_symbols:
            combined_rows.append({
                "date": today_str,
                "symbol": h["symbol"],
                "price": h["price"],
                "change": h["change"],
                "change_pct": h["change_pct"],
                "volume": h["volume"],
                "score": h.get("score", 0),
                "news_catalyst": None
            })

    # 3. Add catalysts (attach catalyst text to matching symbols)
    for c in catalysts:
        for row in combined_rows:
            if row["symbol"] == c["symbol"]:
                row["news_catalyst"] = c["headline"]

    # Write daily screener file
    write_json("daily_screener.json", combined_rows)


# ----------------------------
# ENTRY POINT
# ----------------------------
if __name__ == "__main__":
    run_all_scrapers()
