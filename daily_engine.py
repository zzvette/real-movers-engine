import json
import math
import os
from datetime import datetime

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
HISTORY_DIR = "history"

WEIGHTS = {
    "catalysts": 0.30,
    "momentum": 0.25,
    "liquidity": 0.15,
    "trend": 0.15,
    "volatility": 0.10,
    "stability": 0.05,
}

# ---------------------------------------------------------
# LOAD DAILY SCREENER
# ---------------------------------------------------------
def load_screener():
    with open("daily_screener.json") as f:
        return json.load(f)

# ---------------------------------------------------------
# SCORING ENGINE
# ---------------------------------------------------------
def compute_scores(symbol_data, catalysts_data):
    price = symbol_data["price"]
    change_pct = symbol_data["change_pct"]
    volume = symbol_data["volume"]
    high_52 = symbol_data["high_52"]
    low_52 = symbol_data["low_52"]

    catalyst_score = len([
        c for c in catalysts_data
        if c["symbol"] == symbol_data["symbol"]
    ])

    momentum_score = change_pct
    liquidity_score = math.log(max(volume, 1))

    trend_score = (
        (price - low_52) / (high_52 - low_52)
        if high_52 != low_52 else 0
    )

    volatility_score = abs(change_pct) / 100
    stability_score = 1 - min(abs(change_pct) / 200, 1)

    total = (
        catalyst_score * WEIGHTS["catalysts"] +
        momentum_score * WEIGHTS["momentum"] +
        liquidity_score * WEIGHTS["liquidity"] +
        trend_score * WEIGHTS["trend"] +
        volatility_score * WEIGHTS["volatility"] +
        stability_score * WEIGHTS["stability"]
    )

    if total >= 85:
        tier = "A+"
    elif total >= 70:
        tier = "A"
    elif total >= 55:
        tier = "B"
    elif total >= 40:
        tier = "C"
    else:
        tier = "D"

    return {
        "symbol": symbol_data["symbol"],
        "scores": {
            "total": round(total, 2),
            "tier": tier,
            "catalysts": catalyst_score
        }
    }

# ---------------------------------------------------------
# MAIN DAILY ENGINE
# ---------------------------------------------------------
def run_daily_engine():
    data = load_screener()
    signals = data["signals"]

    trending = signals.get("trending", [])
    gainers = signals.get("gainers", [])
    highs = signals.get("highs", [])
    catalysts_data = signals.get("catalysts", [])

    # Combine trending + gainers
    combined = {}
    for item in trending + gainers:
        combined[item["symbol"]] = item

    scored = [
        compute_scores(v, catalysts_data)
        for v in combined.values()
    ]

    scored.sort(key=lambda x: x["scores"]["total"], reverse=True)
    top_3 = scored[:3]

    # Extract today's news
    today_news = []
    for item in catalysts_data:
        for cat in item["catalysts"]:
            today_news.append(cat)

    # Build minimal snapshot
    today = datetime.now().strftime("%Y-%m-%d")
    snapshot = {
        "date": today,
        "top_3": top_3,
        "news": today_news,
        "trending": list(combined.keys()),
        "gainers": [g["symbol"] for g in gainers],
        "highs": highs
    }

    # Save snapshot
    os.makedirs(HISTORY_DIR, exist_ok=True)
    out_path = os.path.join(HISTORY_DIR, f"{today}.json")

    with open(out_path, "w") as f:
        json.dump(snapshot, f, indent=4)

    print(f"Saved snapshot: {out_path}")

if __name__ == "__main__":
    run_daily_engine()

