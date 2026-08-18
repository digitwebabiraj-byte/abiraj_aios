"""Live progress of the REQ-29 rating collection. Read-only — safe to run any time.

    python avm_status.py            one snapshot
    python avm_status.py --watch    refreshes every 30s until you press Ctrl+C
"""
import json, sys, time
from collections import Counter
from pathlib import Path

CACHE = Path(__file__).resolve().parent / "avm_ratings_cache.json"
TARGET = 1603          # Active ASINs in the 150-family pilot universe


def snapshot():
    if not CACHE.exists():
        return "cache not created yet — the scrape has not written anything"
    d = json.loads(CACHE.read_text())
    c = Counter(v["status"].split(":")[0] for v in d.values())
    ok, nore = c.get("ok", 0), c.get("no_reviews", 0)
    skipped, err = c.get("skipped", 0), c.get("error", 0)
    done = ok + nore + skipped
    pct = 100.0 * done / TARGET
    bar = "#" * int(pct / 2.5) + "." * (40 - int(pct / 2.5))
    rated = [v for v in d.values() if v["status"] == "ok" and v["rating"] is not None]
    avg = sum(v["rating"] for v in rated) / len(rated) if rated else 0
    return "\n".join([
        f"[{bar}] {pct:5.1f}%   {done} of {TARGET}",
        f"  with reviews      {ok:5}   (avg rating {avg:.2f})",
        f"  no reviews at all {nore:5}   <- the merge candidates",
        f"  skipped (family already merged) {skipped:5}",
        f"  errors / blocked  {err:5}",
        f"  last fetched      {max((v['fetched_at'] for v in d.values()), default='-')}",
    ])


if __name__ == "__main__":
    if "--watch" in sys.argv:
        try:
            while True:
                print("\033[2J\033[H" + time.strftime("%H:%M:%S") + "\n" + snapshot(), flush=True)
                time.sleep(30)
        except KeyboardInterrupt:
            print("\nstopped watching (the scrape keeps running)")
    else:
        print(snapshot())
