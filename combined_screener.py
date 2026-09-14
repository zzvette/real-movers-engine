# combined_screener.py

import datetime
from reversal_engine import score_signal


# ---------------------------------------------------------
# SCORING WRAPPER FOR GAINERS
# ---------------------------------------------------------
def score_entry_for_symbol(entry, catalysts):
    """
    Apply your strict scoring engine to a gainers entry.
    This keeps the scoring logic centralized and consistent.
    """

    return score_signal(
        price=entry.get("price"),
        change_pct=entry.get("change_pct"),
        volume=entry.get("volume"),
        catalysts=catalysts,
        premarket=False
    )


# ---------------------------------------------------------
# OPTIONAL: GROUP BY DAY FOR CALENDAR (placeholder)
# ---------------------------------------------------------
def group_by_day(signals):
    """
    Calendar expects:
        { day_number: [raw_symbol_dict, ...] }

    Your GitHub runner currently writes an empty calendar,
    but this function is kept for future expansion.
    """

    today = datetime.date.today()
    day_num = today.day

    grouped = {day_num: []}

    for sig in signals:
        grouped[day_num].append(sig)

    return grouped


# ---------------------------------------------------------
# BUILD COMBINED SCREENER (NOT USED DIRECTLY BY WORKFLOW)
# ---------------------------------------------------------
def build_combined_screener(
    top_gainers,
    top_52week,
    catalyst_log
):
    """
    This function is NOT used directly by your GitHub workflow anymore,
    but it is kept for modularity and future expansion.

    It merges:
    - Top Gainers
    - 52-Week Gainers
    - Catalyst Log
    - Scoring
    """

    # Score gainers
    for entry in top_gainers:
        sym = entry["symbol"]
        catalysts = catalyst_log.get(sym, [])
        entry["score"] = score_entry_for_symbol(entry, catalysts)

    # Score 52-week gainers
    for entry in top_52week:
        sym = entry["symbol"]
        catalysts = catalyst_log.get(sym, [])
        entry["score"] = score_entry_for_symbol(entry, catalysts)

    # Build calendar placeholder
    raw_by_day = group_by_day(top_gainers + top_52week)

    return {
        "top_gainers": top_gainers,
        "top_52week": top_52week,
        "catalyst_log": catalyst_log,
        "raw_by_day": raw_by_day
    }
