# reversal_engine.py

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class SymbolSignal:
    symbol: str
    score: float
    price: float
    change: float
    change_pct: float
    volume: int
    indicator_color: str  # "green", "yellow", "red"
    catalysts: List[Dict[str, Any]] = None


# ---------------------------------------------------------
# SCORING ENGINE
# ---------------------------------------------------------
def score_signal(price, change_pct, volume, catalysts=None):
    """
    Simple scoring model for external scrapers.
    You can tune this later.
    """

    catalysts = catalysts or []

    score = 0

    # Price movement
    score += change_pct * 10     # +1% = +10 points

    # Volume weighting
    if volume > 5_000_000:
        score += 20
    elif volume > 1_000_000:
        score += 10
    else:
        score += 2

    # Catalyst boost
    if len(catalysts) > 0:
        score += 15

    # Clamp score
    if score < 0:
        score = 0
    if score > 100:
        score = 100

    return score


# ---------------------------------------------------------
# RANKING ENGINE (used by calendar)
# ---------------------------------------------------------
def get_top_signals_for_day(raw_list: List[dict], top_n: int = 4) -> List[SymbolSignal]:
    """
    Convert raw JSON entries for a day into SymbolSignal objects,
    sorted by score descending, limited to top_n.
    """
    signals: List[SymbolSignal] = []

    for r in raw_list:
        try:
            symbol = r.get("symbol", "")
            score = float(r.get("score", 0.0))
            price = float(r.get("price", 0.0))
            change = float(r.get("change", 0.0))
            change_pct = float(r.get("change_pct", 0.0))
            volume = int(r.get("volume", 0))
            indicator_color = r.get("indicator_color", "yellow")
            catalysts = r.get("catalysts", [])
        except Exception:
            continue

        signals.append(
            SymbolSignal(
                symbol=symbol,
                score=score,
                price=price,
                change=change,
                change_pct=change_pct,
                volume=volume,
                indicator_color=indicator_color,
                catalysts=catalysts,
            )
        )

    signals.sort(key=lambda s: s.score, reverse=True)
    return signals[:top_n]
