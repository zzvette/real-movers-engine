# combined_screener.py

import datetime
from typing import Tuple, Dict, Any, List

from external_scraper import (
    scrape_tradingview_premarket,
    scrape_yahoo_premarket,
)
from reversal_engine import score_signal


def build_combined_screener(
    premarket: bool = True,
) -> Tuple[
    Dict[int, List[Dict[str, Any]]],  # raw_by_day
    List[Dict[str, Any]],             # real_movers
    Dict[str, Any]                    # catalyst_log
]:
    """
    Build combined screener output.

    premarket=True:
        - Uses TradingView + Yahoo pre-market movers
        - Relaxes volume/change filters
    """

    today = datetime.date.today()
    day_num = today.day

    # -----------------------------------------------------
    # 1. Collect raw symbols from TradingView + Yahoo
    # -----------------------------------------------------
    raw_symbols: List[Dict[str, Any]] = []

    tv_pm = scrape_tradingview_premarket(limit=120)
    raw_symbols.extend(tv_pm)

    yahoo_pm = scrape_yahoo_premarket(limit=60)
    raw_symbols.extend(yahoo_pm)

    # Deduplicate by symbol
    seen = set()
    unique_symbols: List[Dict[str, Any]] = []
    for r in raw_symbols:
        sym = r.get("symbol")
        if not sym or sym in seen:
            continue
        seen.add(sym)
        unique_symbols.append(r)

    raw_symbols = unique_symbols

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
        change = r.get("change", 0.0)

        if not symbol or price is None or change_pct is None:
            continue

        # Pre-market: allow small moves and low volume, but avoid total garbage
        if premarket:
            if abs(change_pct) < 0.3 and volume < 10_000:
                continue
        else:
            if abs(change_pct) < 0.5:
                continue
            if volume < 50_000:
                continue

        catalysts: List[Dict[str, Any]] = []  # placeholder for future

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
            "change": change,
            "change_pct": change_pct,
            "volume": volume,
            "score": score,
            "indicator_color": indicator_color,
            "catalysts": catalysts,
        }

        raw_by_day[day_num].append(entry)
        real_movers.append(entry)

    real_movers.sort(key=lambda x: x["score"], reverse=True)

    return raw_by_day, real_movers, catalyst_log
