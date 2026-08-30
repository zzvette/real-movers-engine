import requests
import pandas as pd
from bs4 import BeautifulSoup
import json
from datetime import datetime

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
MIN_PRICE = 3.0
MIN_VOLUME = 1_000_000
MIN_AVG_VOLUME = 500_000
MAX_FLOAT = 300_000_000  # avoid thin floats
PUMP_KEYWORDS = ["discord", "alert", "pump", "room", "signal"]


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------
def fetch_yahoo_trending():
    url = "https://finance.yahoo.com/trending-tickers"
    resp = requests.get(url, timeout=10)
    tables = pd.read_html(resp.text)
    if not tables:
        return []
    df = tables[0]
    df.rename(columns={"Symbol": "symbol"}, inplace=True)
    return df.to_dict(orient="records")


def fetch_finviz_table(view_code):
    url = f"https://finviz.com/screener.ashx?v={view_code}&t="
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(resp.text, "html.parser")
    tables = soup.find_all("table")
    if not tables:
        return []

    df_list = pd.read_html(str(tables[-1]))
    if not df_list:
        return []

    df = df_list[0]
    if "Ticker" not in df.columns:
        return []

    df.rename(columns={"Ticker": "symbol"}, inplace=True)
    return df.to_dict(orient="records")


def safe_float(val):
    try:
        return float(str(val).replace(",", "").replace("%", ""))
    except:
        return None


# ---------------------------------------------------------
# FILTERS
# ---------------------------------------------------------
def passes_filters(entry):
    price = safe_float(entry.get("Price"))
    volume = safe_float(entry.get("Volume"))
    avg_vol = safe_float(entry.get("Avg Vol (3 month)"))
    float_shares = safe_float(entry.get("Float"))

    if price is not None and price < MIN_PRICE:
        return False

    if volume is not None and volume < MIN_VOLUME:
        return False

    if avg_vol is not None and avg_vol < MIN_AVG_VOLUME:
        return False

    if float_shares is not None and float_shares < MAX_FLOAT:
        pass  # good
    else:
        return False

    return True


# ---------------------------------------------------------
# SCORING
# ---------------------------------------------------------
def score_ticker(entry):
    score = 0

    price = safe_float(entry.get("Price"))
    volume = safe_float(entry.get("Volume"))
    change_pct = safe_float(entry.get("Change %"))

    # Price score
    if price:
        if price > 10:
            score += 10
        if price > 20:
            score += 10

    # Volume score
    if volume:
        if volume > 2_000_000:
            score += 15
        if volume > 5_000_000:
            score += 20

    # Momentum score
    if change_pct:
        if change_pct > 3:
            score += 10
        if change_pct > 7:
            score += 15

    return min(score, 100)


# ---------------------------------------------------------
# MAIN ENGINE
# ---------------------------------------------------------
def build_real_movers():
    yahoo = fetch_yahoo_trending()
    finviz_gainers = fetch_finviz_table(152)
    finviz_active = fetch_finviz_table(111)

    all_entries = {}

    # Merge sources
    for source_name, source_data in [
        ("yahoo_trending", yahoo),
        ("finviz_gainers", finviz_gainers),
        ("finviz_active", finviz_active),
    ]:
        for row in source_data:
            sym = row.get("symbol")
            if not sym:
                continue
            if sym not in all_entries:
                all_entries[sym] = {"symbol": sym, "sources": set(), "raw": []}
            all_entries[sym]["sources"].add(source_name)
            all_entries[sym]["raw"].append(row)

    # Build final list
    movers = []
    for sym, info in all_entries.items():
        first = info["raw"][0]

        # Apply filters
        if not passes_filters(first):
            continue

        entry = {
            "symbol": sym,
            "sources": list(info["sources"]),
            "score": score_ticker(first),
            "meta": {},
        }

        for k in ["Price", "Change", "Change %", "Volume", "Avg Vol (3 month)", "Float"]:
            if k in first:
                entry["meta"][k] = first[k]

        movers.append(entry)

    movers.sort(key=lambda x: x["score"], reverse=True)

    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "count": len(movers),
        "movers": movers,
    }

    with open("real_movers.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


if __name__ == "__main__":
    build_real_movers()
