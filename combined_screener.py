# combined_screener.py

import datetime
from typing import Tuple, Dict, Any, List

from external_scraper import (
    scrape_finviz_gainers,
    scrape_finviz_losers,
    scrape_yahoo_premarket,
)
from reversal_engine import score_signal


# ---------------------------------------------------------
# BUILD COMBINED SCREENER
# ---------------------------------------------------------
def build_combined_screener(premarket: bool = True) -> Tuple[
    Dict[int, List[Dict[str, Any]]],  # raw_by_day
    List[Dict[str, Any]],             # real_movers
    Dict[str, Any]                    # catalyst_log
]:
    """
    Build combined screener output.

    premarket=True:
        - Uses Yahoo premarket gainers
        - Relaxes volume/change filters
    """

    today = datetime.date.today()
    day_num = today.day

    # -----------------------------------------------------
    # 1. Collect raw symbols
    # -----------------------------------------------------
    raw_symbols: List[Dict[str, Any]] = []

    if premarket:
        yahoo_pm = scrape_yahoo_premarket()
        raw_symbols.extend(yahoo_pm)
    else:
        gainers = scrape_finviz_gainers()
        losers = scrape_finviz_losers()
        raw_symbols.extend(gainers)
        raw_symbols.extend(losers)

    # -----------------------------------------------------
    # 2. Filter and score
    # -----------------------------------------------------
    real_movers: List[Dict[str, Any]] = []
    raw_by_day: Dict[int, List[Dict[str, Any]]] = {day_num: []}
    catalyst_log: Dict[str, Any] = {"catalysts": {}}

    for r in raw_symbols:
        symbol = r.get("symbol")
        price = r.get("price")
        change_pct = r.get("change_pct")
        volume = r.get("volume", 0)

        # Basic sanity checks
        if not symbol or price is None or change_pct is None:
            continue

        # Relaxed premarket filters: allow small moves and low volume
        if not premarket:
            if abs(change_pct) < 0.5:
                continue
            if volume < 50_000:
                continue

        # No catalysts yet in this version
        catalysts: List[Dict[str, Any]] = []

        score = score_signal(
            price=price,
            change_pct=change_pct,
            volume=volume,
            catalysts=catalysts,
            premarket=premarket,
        )

        if score <= 0:
            continue

        indicator_color = (
            "green" if score >= 70 else
            "yellow" if score >= 40 else
            "red"
        )

        entry = {
            "symbol": symbol,
            "price": price,
            "change": r.get("change", 0.0),
            "change_pct": change_pct,
            "volume": volume,
            "score": score,
            "indicator_color": indicator_color,
            "catalysts": catalysts,
        }

        raw_by_day[day_num].append(entry)
        real_movers.append(entry)

    # Sort real movers by score
    real_movers.sort(key=lambda x: x["score"], reverse=True)

    return raw_by_day, real_movers, catalyst_log
