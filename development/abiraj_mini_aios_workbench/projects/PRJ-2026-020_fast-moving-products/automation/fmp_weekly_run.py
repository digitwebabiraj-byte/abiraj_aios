# -*- coding: utf-8 -*-
"""FMP weekly auto-refresh (REQ-23-D01) — fail-closed.
Refreshes the Fast Moving Products Excel + HTML dashboard from the RAW mcp.ledsone DB.
Does NOT publish to ph_task (held pending Mahima's audience/sign-off).

Pipeline: fmp_fetch_raw.py (raw psycopg2 fetch -> fmp_payload.json) -> build_fmp_d01.py (xlsx)
-> gen_dashboard.py (html). Gates the fresh payload before overwriting the delivered outputs;
on any failure it leaves the last-good outputs untouched and writes an alert.
"""
import os, sys, json, shutil, subprocess, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
SQL  = os.path.join(PROJ, "sql", "REQ-23_fast-moving-products")
OUT  = os.path.join(PROJ, "evidence", "final_outputs", "REQ-23_fast-moving-products")
STATUS = os.path.join(HERE, "fmp_status.txt")
LASTGOOD = os.path.join(HERE, "fmp_last_good.json")
ALERT = os.path.join(os.path.expanduser("~"), "Desktop", "FMP_ALERT.txt")

ROW_FLOOR = 10          # each channel/combined must have >= this many ranked rows
COLLAPSE_FRAC = 0.60    # fail if fresh row count < 60% of last good (data collapse guard)
CHANNELS = ("amazon", "ebay", "shopify", "combined")

def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(STATUS, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def alert(msg):
    with open(ALERT, "w", encoding="utf-8") as f:
        f.write(f"FMP weekly refresh FAILED {datetime.datetime.now():%Y-%m-%d %H:%M}\n{msg}\n"
                f"Outputs were NOT overwritten (last-good preserved). See {STATUS}\n")
    log("ALERT: " + msg)

def run(script):
    r = subprocess.run([sys.executable, os.path.join(SQL, script)], cwd=SQL,
                       capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        raise RuntimeError(f"{script} failed: {r.stderr.strip()[:500]}")
    return r.stdout.strip()

def main():
    log("=== FMP weekly refresh start ===")
    # 1. fetch from RAW mcp.ledsone (needs LED_* env from secrets.bat)
    for v in ("LED_PGHOST", "LED_PGUSER", "LED_PGPASSWORD"):
        if not os.environ.get(v):
            alert(f"missing credential env var {v}"); return 1
    try:
        log("fetch: " + run("fmp_fetch_raw.py"))
    except Exception as e:
        alert(f"raw fetch failed: {e}"); return 1

    # 2. gate the fresh payload BEFORE building
    payload = json.load(open(os.path.join(SQL, "fmp_payload.json"), encoding="utf-8"))
    counts = {c: len(payload.get(c, [])) for c in CHANNELS}
    log("row counts: " + json.dumps(counts))
    for c in CHANNELS:
        if counts[c] < ROW_FLOOR:
            alert(f"row-floor gate: {c} has {counts[c]} < {ROW_FLOOR}"); return 1
    if os.path.exists(LASTGOOD):
        prev = json.load(open(LASTGOOD, encoding="utf-8"))
        for c in CHANNELS:
            if prev.get(c, 0) and counts[c] < COLLAPSE_FRAC * prev[c]:
                alert(f"collapse gate: {c} {counts[c]} < {COLLAPSE_FRAC:.0%} of last-good {prev[c]}"); return 1

    # 3. build xlsx + dashboard
    try:
        run("build_fmp_d01.py"); run("gen_dashboard.py")
    except Exception as e:
        alert(f"build failed: {e}"); return 1

    # 4. publish outputs to evidence/final_outputs (atomic-ish copy)
    os.makedirs(OUT, exist_ok=True)
    for fn in ("REQ-23-D01_fast_moving_products.xlsx", "REQ-23-D01_fast_moving_products.html"):
        src = os.path.join(SQL, fn)
        if not os.path.exists(src):
            alert(f"expected output missing: {fn}"); return 1
        shutil.copyfile(src, os.path.join(OUT, fn))
    json.dump(counts, open(LASTGOOD, "w", encoding="utf-8"))
    if os.path.exists(ALERT):
        os.remove(ALERT)
    log(f"OK — refreshed Excel + dashboard for window {payload['meta']['win30_start']}"
        f" -> {payload['meta']['win_end']}. ph_task publish NOT run (held for Mahima).")
    log("=== FMP weekly refresh done ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
