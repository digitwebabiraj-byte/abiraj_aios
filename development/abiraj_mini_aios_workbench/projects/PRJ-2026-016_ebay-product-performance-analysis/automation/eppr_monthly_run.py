# -*- coding: utf-8 -*-
"""
REQ-19-D02 — monthly unattended refresh of the eBay Product Performance report.
Rebuilds the static NO-JS portal HTML from live data and refreshes the ph_task rows (472-475) in place.

FAIL-CLOSED: on any bad pull it refuses to publish and leaves the last good rows untouched, writes
a FAILED status, and exits non-zero so the wrapper raises a Desktop alert. A stale-but-correct report
beats a fresh wrong one. Read-only on all source data; the only write is the guarded ph_task refresh.
Credentials come from the environment (set by run_eppr_monthly.bat / the shared global store).
"""
import os, sys, json, datetime, hashlib, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "sql", "REQ-19_ebay-product-performance-analysis"))

STATUS  = os.path.join(HERE, "eppr_status.txt")
LASTGOOD = os.path.join(HERE, "eppr_last_good.json")
LOG      = os.path.join(HERE, "eppr_run.log")
HTML     = os.path.abspath(os.path.join(HERE, "..","evidence","final_outputs",
           "REQ-19_ebay-product-performance-analysis","REQ-19-D01_ph_task.html"))

MIN_ROWS = 8000          # baseline ~11,100; refuse if the universe collapses below this
COLLAPSE = 0.60          # refuse if rows < 60% of the last good run

def log(msg):
    line = "%s  %s" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg)
    print(line)
    with open(LOG, "a", encoding="utf-8") as f: f.write(line + "\n")

def write_status(state, detail):
    with open(STATUS, "w", encoding="utf-8") as f:
        f.write("%s | %s | %s\n" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), state, detail))

def last_good_rows():
    try:
        with open(LASTGOOD, encoding="utf-8") as f: return json.load(f).get("rows", 0)
    except Exception: return 0

def main():
    log("=== EPPR monthly run START ===")
    try:
        from render_eppr_static import render
        from publish_eppr_ph_task import main as publish

        n = render()                                   # rebuild the static portal HTML from live data
        log("rebuilt static HTML: %d rows" % n)

        prev = last_good_rows()
        # ---- fail-closed gates ----
        if n == 0:
            raise RuntimeError("GATE FAIL: 0 rows returned — not publishing")
        if n < MIN_ROWS:
            raise RuntimeError("GATE FAIL: %d rows < MIN_ROWS %d — not publishing" % (n, MIN_ROWS))
        if prev and n < COLLAPSE * prev:
            raise RuntimeError("GATE FAIL: %d rows < %.0f%% of last good %d — not publishing" % (n, COLLAPSE*100, prev))
        if not os.path.exists(HTML) or os.path.getsize(HTML) < 1_000_000:
            raise RuntimeError("GATE FAIL: static HTML missing or too small — not publishing")
        log("gates PASS (rows=%d, last_good=%d)" % (n, prev))

        publish(commit=True)                           # guarded refresh of ph_task 472-475 (version bump)
        md5 = hashlib.md5(open(HTML, "rb").read()).hexdigest()
        with open(LASTGOOD, "w", encoding="utf-8") as f:
            json.dump({"rows": n, "md5": md5, "when": datetime.datetime.now().isoformat()}, f)
        write_status("OK", "published ph_task 472-475 · %d rows · md5 %s" % (n, md5[:8]))
        log("=== EPPR monthly run OK (published, %d rows) ===" % n)
        return 0
    except Exception as e:
        log("FAILED: %s" % e)
        log(traceback.format_exc())
        write_status("FAILED", str(e).splitlines()[0])
        return 1

if __name__ == "__main__":
    sys.exit(main())
