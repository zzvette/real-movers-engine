from typing import List, Dict
from datetime import datetime, timezone

INSTITUTIONAL_KEYWORDS = [
    "earnings", "guidance", "sec", "filing", "merger",
    "acquisition", "offering", "partnership", "approval",
    "downgrade", "upgrade"
]

RETAIL_KEYWORDS = [
    "why", "should you buy", "opinion", "blog", "hype"
]


def score_catalyst(item: Dict) -> Dict:
    title = (item.get("title") or "").lower()
    publisher = (item.get("publisher") or "").lower()

    strength = 0
    institutional = 0.0
    momentum = 0.0

    # Base strength from publisher quality
    if any(p in publisher for p in ["reuters", "bloomberg", "marketwatch", "seeking alpha", "yahoo finance"]):
        strength += 30
    else:
        strength += 10

    # Keyword‑based institutional scoring
    inst_hits = sum(1 for kw in INSTITUTIONAL_KEYWORDS if kw in title)
    retail_hits = sum(1 for kw in RETAIL_KEYWORDS if kw in title)

    strength += inst_hits * 10
    strength -= retail_hits * 5

    institutional = min(1.0, 0.2 * inst_hits)
    institutional = max(0.0, institutional)

    # Momentum: recency + density placeholder
    # If providerPublishTime exists, use it; otherwise use scrape_timestamp
    ts = item.get("published_at") or item.get("scrape_timestamp")
    try:
        ts_dt = datetime.fromtimestamp(ts, tz=timezone.utc) if isinstance(ts, (int, float)) else datetime.fromisoformat(ts)
    except Exception:
        ts_dt = datetime.now(timezone.utc)

    age_minutes = (datetime.now(timezone.utc) - ts_dt).total_seconds() / 60.0
    if age_minutes < 15:
        momentum += 40
    elif age_minutes < 60:
        momentum += 25
    elif age_minutes < 180:
        momentum += 10

    # Combine
    strength = max(0, min(100, strength))
    momentum = max(0, min(100, momentum))

    item["strength_score"] = strength
    item["institutional_score"] = institutional
    item["momentum_score"] = momentum

    return item


def score_all_catalysts(catalysts: List[Dict]) -> List[Dict]:
    return [score_catalyst(c) for c in catalysts]
