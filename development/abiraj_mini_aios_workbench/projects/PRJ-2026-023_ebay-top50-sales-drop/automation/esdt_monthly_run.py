# -*- coding: utf-8 -*-
"""ESDT monthly auto-refresh (REQ-26-D01) — fail-closed.
Rebuilds the eBay UK Top 50 Sales Drop Excel + dashboard from the live raw ledsone DB (the
SQL uses CURRENT_DATE, so each run is the fresh last-30d-vs-previous-30d window), then — if
publish creds are present — refreshes all published portal rows (project_code='esdt').

Pipeline: build_esdt_d01.py (raw psycopg2 fetch -> esdt_payload.json + xlsx) then
render_esdt_dashboard.py (-> html). The fresh payload is gated (row-floor + collapse guard)
and the outputs are size-checked; on ANY failure the last-good outputs are restored and an
alert is written — the portal rows are never refreshed with a bad build.
"""
import os, sys, json, shutil, subprocess, datetime, hashlib, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
SQL  = os.path.join(PROJ, "sql", "REQ-26_ebay-top50-sales-drop")
OUT  = os.path.join(PROJ, "evidence", "final_outputs", "REQ-26_ebay-top50-sales-drop")
BUILD   = os.path.join(SQL, "build_esdt_d01.py")
RENDER  = os.path.join(SQL, "render_esdt_dashboard.py")
PUBLISH = os.path.join(HERE, "publish_esdt_ph_task.py")
PAYLOAD = os.path.join(SQL, "esdt_payload.json")
XLSX = os.path.join(OUT, "REQ-26-D01_ebay_top50_sales_drop.xlsx")
HTML = os.path.join(OUT, "REQ-26-D01_ebay_top50_sales_drop.html")
STATUS   = os.path.join(HERE, "esdt_status.txt")
LASTGOOD = os.path.join(HERE, "esdt_last_good.json")
ALERT = os.path.join(os.path.expanduser("~"), "Desktop", "ESDT_ALERT.txt")

ROW_FLOOR     = 20     # Top-50 report; fail if fewer than this many qualifying SKUs
COLLAPSE_FRAC = 0.50   # fail if fresh count < 50% of last-good

def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"; print(line)
    with open(STATUS, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def alert(msg):
    with open(ALERT, "w", encoding="utf-8") as f:
        f.write(f"ESDT monthly refresh FAILED {datetime.datetime.now():%Y-%m-%d %H:%M}\n{msg}\n"
                f"Outputs restored to last-good; portal rows NOT refreshed. See {STATUS}\n")
    log("ALERT: " + msg)

def _lastgood_rows():
    if not os.path.exists(LASTGOOD): return 0
    try: return json.load(open(LASTGOOD, encoding="utf-8")).get("rows", 0)
    except Exception: return 0

def _run(script, cwd, timeout):
    return subprocess.run([sys.executable, script], cwd=cwd, capture_output=True, text=True, timeout=timeout)

def main():
    log("=== ESDT monthly refresh start ===")
    for v in ("LED_PGHOST", "LED_PGUSER", "LED_PGPASSWORD"):
        if not os.environ.get(v):
            alert(f"missing credential env var {v}"); return 1

    bak = {}
    for p in (XLSX, HTML):
        if os.path.exists(p):
            bak[p] = p + ".bak"; shutil.copyfile(p, bak[p])
    def restore():
        for p, b in bak.items():
            if os.path.exists(b): shutil.copyfile(b, p)

    # 1. rebuild data + Excel
    try:
        r = _run(BUILD, SQL, 900)
        if r.returncode != 0:
            restore(); alert(f"build failed: {r.stderr.strip()[:500]}"); return 1
        log("build: " + (r.stdout.strip().splitlines() or ["(no output)"])[0])
    except Exception as e:
        restore(); alert(f"build crashed: {e}"); return 1

    # 2. render HTML dashboard
    try:
        r = _run(RENDER, SQL, 300)
        if r.returncode != 0:
            restore(); alert(f"render failed: {r.stderr.strip()[:500]}"); return 1
        log("render: " + (r.stdout.strip().splitlines() or ["(no output)"])[0])
    except Exception as e:
        restore(); alert(f"render crashed: {e}"); return 1

    # 3. gate the fresh payload
    try:
        rows = len(json.load(open(PAYLOAD, encoding="utf-8"))["rows"])
    except Exception as e:
        restore(); alert(f"cannot read payload: {e}"); return 1
    log(f"rows: {rows}")
    if rows < ROW_FLOOR:
        restore(); alert(f"row-floor gate: {rows} < {ROW_FLOOR}"); return 1
    prev = _lastgood_rows()
    if prev and rows < COLLAPSE_FRAC * prev:
        restore(); alert(f"collapse gate: {rows} < {COLLAPSE_FRAC:.0%} of last-good {prev}"); return 1

    # 4. size-check outputs
    for p, floor in ((XLSX, 15000), (HTML, 40000)):
        if not os.path.exists(p) or os.path.getsize(p) < floor:
            restore(); alert(f"output too small/missing: {os.path.basename(p)}"); return 1
    md5 = hashlib.md5(open(HTML, "rb").read()).hexdigest()
    json.dump({"rows": rows, "html_md5": md5, "at": f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}"},
              open(LASTGOOD, "w", encoding="utf-8"))

    # 5. refresh all published portal rows (only if publish creds present)
    if os.environ.get("PGPASSWORD"):
        try:
            r = _run_publish()
            if r.returncode != 0:
                alert(f"portal refresh failed (build OK): {r.stderr.strip()[:400]}"); return 1
            log("portal rows refreshed (--refresh): " + (r.stdout.strip().splitlines() or [""])[-1])
        except Exception as e:
            alert(f"portal refresh crashed (build OK): {e}"); return 1
    else:
        log("PGPASSWORD not set — skipped portal refresh (outputs refreshed only).")

    for b in bak.values():
        if os.path.exists(b): os.remove(b)
    if os.path.exists(ALERT): os.remove(ALERT)
    log(f"OK — {rows} rows, html md5 {md5[:8]}.")
    log("=== ESDT monthly refresh done ===")
    return 0

def _run_publish():
    return subprocess.run([sys.executable, PUBLISH, "--refresh"], cwd=HERE,
                          capture_output=True, text=True, timeout=180)

if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception:
        tb = traceback.format_exc()
        alert("ESDT monthly crashed — see esdt_status.txt\n" + tb.splitlines()[-1])
        log("CRASH:\n" + tb); sys.exit(1)
