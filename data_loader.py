# data_loader.py

import requests
from datetime import datetime

GITHUB_URL="https://raw.githubusercontent.com/zzvette/real-movers-engine/main/real_movers.json"

def load_raw_data_for_month(year: int, month: int):
    """
    Expected GitHub JSON format:
    [
        {
            "symbol": "TSLA",
            "timestamp": "2026-09-11T09:30:00",
            "reversal_score": 78,
            "divergence": true,
            "market_structure_break": true,
            "volume_spike": "Moderate",
            "news_catalyst": null,
            "atr_regime": "Normal",
            "crowd_risk": "Low"
        },
        ...
    ]
    """

    try:
        response = requests.get(GITHUB_URL, timeout=5)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print("Error loading GitHub data:", e)
        return {}

    # Organize by day number
    raw_by_day = {}

    for entry in data:
        ts = entry.get("timestamp")
        if not ts:
            continue

        dt = datetime.fromisoformat(ts)
        if dt.year == year and dt.month == month:
            day_num = dt.day
            raw_by_day.setdefault(day_num, []).append(entry)

    return raw_by_day
