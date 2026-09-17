import json
from pathlib import Path
from datetime import datetime, timezone

from news_scraper import fetch_catalysts
from daily_engine import score_all_catalysts


def get_symbols_for_scan() -> list:
    """
    For now, pull from daily_screener.json or top_gainers.json.
    You can refine this later.
    """
    symbols = set()

    for fname in ["daily_screener.json", "top_gainers.json", "top_52week.json"]:
        p = Path(fname)
        if p.exists():
            try:
                data = json.loads(p.read_text())
                for item in data:
                    sym = item.get("symbol") or item.get("ticker")
                    if sym:
                        symbols.add(sym)
            except Exception as e:
                print(f"[WARN] Failed to read {fname}: {e}")

    return sorted(symbols)


def main():
    repo_root = Path(__file__).resolve().parent
    catalysts_dir = repo_root / "catalysts"
    catalysts_dir.mkdir(exist_ok=True)

    symbols = get_symbols_for_scan()
    if not symbols:
        print("[WARN] No symbols found for scan.")
        return

    print(f"[INFO] Scanning {len(symbols)} symbols for news...")
    raw_catalysts = fetch_catalysts(symbols)
    scored_catalysts = score_all_catalysts(raw_catalysts)

    # Timestamp for filename
    now = datetime.now(timezone.utc)
    ts_str = now.strftime("%Y%m%d_%H%M%S")

    snapshot_path = catalysts_dir / f"{ts_str}.json"
    latest_path = catalysts_dir / "latest.json"

    snapshot_path.write_text(json.dumps(scored_catalysts, indent=2))
    latest_path.write_text(json.dumps(scored_catalysts, indent=2))

    print(f"[INFO] Wrote snapshot: {snapshot_path}")
    print(f"[INFO] Updated latest: {latest_path}")


if __name__ == "__main__":
    main()
