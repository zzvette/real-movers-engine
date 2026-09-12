# reversal_engine.py

from dataclasses import dataclass
from typing import List


@dataclass
class SymbolSignal:
    symbol: str
    score: float
    price: float
    change: float
    change_pct: float
    volume: int
    indicator_color: str  # "green", "yellow", "red"


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
            )
        )

    signals.sort(key=lambda s: s.score, reverse=True)
    return signals[:top_n]
