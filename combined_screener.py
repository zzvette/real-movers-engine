# combined_screener.py

import datetime
from typing import List, Dict, Any, Tuple

from external_scraper import get_external_screener_data
from reversal_engine import SymbolSignal, score_signal


# ---------------------------------------------------------
# NORMALIZATION
# ---------------------------------------------------------
def normalize_row(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize raw scraped fields into a consistent structure.
    """
    return {
        "symbol": row.get("symbol"),
        "price": row.get("price"),
        "change_pct": row.get("change_pct"),
        "volume": row.get("volume"),
        "source": row.get("source"),
    }


# ---------------------------------------------------------
# SCORING + SIGNAL CREATION
# ---------------------------------------------------------
def build_symbol_signal(row: Dict[str, Any],
                        catalysts: List[Dict[str, Any]]) -> SymbolSignal:
    """
    Convert normalized row + catalysts into a SymbolSignal object.
    """
    symbol = row["symbol"]

    # Score using your reversal engine logic
    score = score_signal(
        price=row.get("price"),
        change_pct=row.get("change_pct"),
        volume=row.get("volume"),
        catalysts=catalysts
    )

    # Determine indicator color
    if score >= 80:
        color = "green"
    elif score >= 50:
        color = "yellow"
    else:
        color = "red"

    return SymbolSignal(
        symbol=symbol,
        indicator_color=color,
        score=score,
        price=row.get("price"),
        change=row.get("change_pct"),  # optional
        change_pct=row.get("change_pct"),
        volume=row.get("volume"),
        catalysts=catalysts
    )


# ---------------------------------------------------------
# GROUP BY DAY FOR CALENDAR
# ---------------------------------------------------------
def group_by_day(signals: List[SymbolSignal]) -> Dict[int, List[Dict[str, Any]]]:
    """
    Calendar expects:
        { day_number: [raw_symbol_dict, ...] }
    """

    today = datetime.date.today()
    year = today.year
    month = today.month

    grouped: Dict[int, List[Dict[str, Any]]] = {}

    for sig in signals:
        # For now, all signals belong to "today"
        # Later we will expand this to historical or multi-day data
        day_num = today.day

        if day_num not in grouped:
            grouped[day_num] = []

        grouped[day_num].append(
            {
                "symbol": sig.symbol,
                "price": sig.price,
                "change_pct": sig.change_pct,
                "volume": sig.volume,
                "score": sig.score,
                "indicator_color": sig.indicator_color,
                "catalysts": sig.catalysts,
            }
        )

    return grouped


# ---------------------------------------------------------
# REAL MOVERS (TOP N)
# ---------------------------------------------------------
def get_real_movers(signals: List[SymbolSignal], top_n: int = 20) -> List[Dict[str, Any]]:
    """
    Real Movers = highest scoring signals across all sources.
    """
    sorted_signals = sorted(signals, key=lambda s: s.score, reverse=True)
    movers = sorted_signals[:top_n]

    return [
        {
            "symbol": s.symbol,
            "score": s.score,
            "price": s.price,
            "change_pct": s.change_pct,
            "volume": s.volume,
            "indicator_color": s.indicator_color,
            "catalysts": s.catalysts,
        }
        for s in movers
    ]


# ---------------------------------------------------------
# CATALYST LOG
# ---------------------------------------------------------
def build_catalyst_log(catalysts_by_symbol: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Build a clean catalyst log for GitHub storage.
    """
    return {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "catalysts": catalysts_by_symbol
    }


# ---------------------------------------------------------
# MASTER COMBINER
# ---------------------------------------------------------
def build_combined_screener() -> Tuple[
    Dict[int, List[Dict[str, Any]]],   # raw_by_day for calendar
    List[Dict[str, Any]],              # real movers
    Dict[str, Any]                     # catalyst log
]:
    """
    Main entry point for your entire external data pipeline.
    """

    # 1. Scrape external data
    raw_rows, catalysts_by_symbol = get_external_screener_data()

    # 2. Normalize
    normalized = [normalize_row(r) for r in raw_rows]

    # 3. Convert to SymbolSignal objects
    signals: List[SymbolSignal] = []
    for row in normalized:
        symbol = row["symbol"]
        cats = catalysts_by_symbol.get(symbol, [])
        sig = build_symbol_signal(row, cats)
        signals.append(sig)

    # 4. Group by day for calendar
    raw_by_day = group_by_day(signals)

    # 5. Real Movers
    real_movers = get_real_movers(signals)

    # 6. Catalyst log
    catalyst_log = build_catalyst_log(catalysts_by_symbol)

    return raw_by_day, real_movers, catalyst_log


# ---------------------------------------------------------
# Standalone test
# ---------------------------------------------------------
if __name__ == "__main__":
    raw_by_day, real_movers, catalyst_log = build_combined_screener()

    print("Calendar-ready raw_by_day:")
    print(raw_by_day)

    print("\nTop Real Movers:")
    for m in real_movers[:10]:
        print(m)

    print("\nCatalyst Log:")
    print(catalyst_log)
