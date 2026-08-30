import requests
import pandas as pd
from bs4 import BeautifulSoup
import json
from datetime import datetime

# ---------- Helpers ----------

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
    # view_code examples:
    # 111 = performance, 152 = top gainers, 111 most active, etc.
    url = f"https://finviz.com/screener.ashx?v={view_code}&t="
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(resp.text, "html.parser")
    tables = soup.find_all("table")
    if not tables:
        return []

    # Finviz main screener table is usually the last one
    df_list = pd.read_html(str(tables[-1]))
    if not df_list:
        return []

    df = df_list[0]
    if "Ticker" not in df.columns:
        return []

    df.rename(columns={"Ticker": "symbol"}, inplace=True)
    return df.to_dict(orient="records")


def score_ticker(entry):
    # Very simple scoring for now; we can refine later
    score = 0

    # Yahoo fields
    change_pct = entry.get("Change %") or entry.get("Perf Week") or ""
    vol = entry.get("Volume") or entry.get("Vol") or ""
    avg_vol = entry.get("Avg Vol (3 month)") or entry.get("Avg Volume") or ""

    # Rough volume score
    try:
        vol_val = float(str(vol).replace(",", "").replace("%", ""))
        if vol_val > 1_000_000:
            score += 20
        if vol_val > 5_000_000:
            score += 30
    except Exception:
        pass

    # Placeholder volatility/catalyst scoring
    score += 10  # base score for being in a trending list

    return min(score, 100)


# ---------- Main engine ----------

def build_real_movers():
    yahoo = fetch_yahoo_trending()
    finviz_gainers = fetch_finviz_table(152)   # top gainers
    finviz_active = fetch_finviz_table(111)    # most active

    all_entries = {}

    # Yahoo
    for row in yahoo:
        sym = row.get("symbol")
        if not sym:
            continue
        if sym not in all_entries:
            all_entries[sym] = {"symbol": sym, "sources": set(), "raw": []}
        all_entries[sym]["sources"].add("yahoo_trending")
        all_entries[sym]["raw"].append(row)

    # Finviz gainers
    for row in finviz_gainers:
        sym = row.get("symbol")
        if not sym:
            continue
        if sym not in all_entries:
            all_entries[sym] = {"symbol": sym, "sources": set(), "raw": []}
        all_entries[sym]["sources"].add("finviz_gainers")
        all_entries[sym]["raw"].append(row)

    # Finviz most active
    for row in finviz_active:
        sym = row.get("symbol")
        if not sym:
            continue
        if sym not in all_entries:
            all_entries[sym] = {"symbol": sym, "sources": set(), "raw": []}
        all_entries[sym]["sources"].add("finviz_active")
        all_entries[sym]["raw"].append(row)

    # Build final list
    movers = []
    for sym, info in all_entries.items():
        entry = {
            "symbol": sym,
            "sources": list(info["sources"]),
            "score": 0,
            "meta": {},
        }

        # Simple scoring: more sources = higher base score
        base = 10 * len(info["sources"])
        entry["score"] = base

        # Try to add some meta fields from first raw record
        if info["raw"]:
            first = info["raw"][0]
            for k in ["Price", "Change", "Change %", "Volume", "Avg Vol (3 month)"]:
                if k in first:
                    entry["meta"][k] = first[k]

        movers.append(entry)

    # Sort by score descending
    movers.sort(key=lambda x: x["score"], reverse=True)

    # Save JSON
    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "count": len(movers),
        "movers": movers,
    }

    with open("real_movers.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


if __name__ == "__main__":
    build_real_movers()
