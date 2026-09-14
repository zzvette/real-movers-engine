# combined_screener.py

import datetime
from typing import Dict, Any, List

from news_scraper import scrape_all_news_sources
from symbol_data_fetcher import fetch_symbol_data
from reversal_engine import score_signal


def build_combined_screener() -> (
    Dict[int, List[Dict[str, Any]]],   # raw_by_day
    List[Dict[str, Any]],              # real_movers
    Dict[str, Any]                     # catalyst_log
):
    """
    Catalyst-first screener:
    1. Pull business news from all N4 sources
    2. Extract tickers
    3. Fetch live stock data
    4. Score strictly
    5. Output strong movers only
    """

    today = datetime.date.today()
    day_num = today.day

    # -----------------------------------------------------
    # 1. Pull all catalyst news
    # -----------------------------------------------------
    news_items = scrape_all_news_sources()

    # Build catalyst log
    catalyst_log = {"catalysts": {}}

    # Extract unique symbols
    symbols = set()
    for item in news_items:
        for sym in item["symbols"]:
            symbols.add(sym)

            # Add to catalyst log
            if sym not in catalyst_log["catalysts"]:
                catalyst_log["catalysts"][sym] = []
            catalyst_log["catalysts"][sym].append({
                "source": item["source"],
                "headline": item["headline"]
            })

    # -----------------------------------------------------
    # 2. Fetch stock data for each symbol
    # -----------------------------------------------------
    raw_by_day = {day_num: []}
    real_movers: List[Dict[str, Any]] = []

    for sym in symbols:
        data = fetch_symbol_data(sym)
        if not data:
            continue

        price = data["price"]
        change = data["change"]
        change_pct = data["change_pct"]
        volume = data["volume"]

        # Strict mode: require meaningful movement
        if abs(change_pct) < 0.5:
            continue
        if volume < 100_000:
            continue

        # -------------------------------------------------
        # 3. Score strictly
        # -------------------------------------------------
        score = score_signal(
            price=price,
            change_pct=change_pct,
            volume=volume,
            catalysts=catalyst_log["catalysts"].get(sym, []),
            premarket=False  # strict catalyst mode
        )

        if score <= 0:
            continue

        indicator_color = (
            "green" if score >= 70 else
            "yellow" if score >= 40 else
            "red"
        )

        entry = {
            "symbol": sym,
            "price": price,
            "change": change,
            "change_pct": change_pct,
            "volume": volume,
            "score": score,
            "indicator_color": indicator_color,
            "catalysts": catalyst_log["catalysts"].get(sym, [])
        }

        raw_by_day[day_num].append(entry)
        real_movers.append(entry)

    # Sort by score
    real_movers.sort(key=lambda x: x["score"], reverse=True)

    return raw_by_day, real_movers, catalyst_log
