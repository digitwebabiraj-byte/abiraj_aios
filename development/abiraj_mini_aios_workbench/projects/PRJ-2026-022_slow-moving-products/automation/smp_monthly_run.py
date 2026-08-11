# -*- coding: utf-8 -*-
"""SMP monthly auto-refresh (REQ-25-D01) — fail-closed.
Rebuilds the Slow Moving Products Excel + teal HTML dashboard from the RAW mcp.ledsone DB,
then (if publish creds are present) refreshes the published portal row ph_task id 735.

Pipeline: build_smp_d01.py (raw psycopg2 fetch -> smp_payload.json + xlsx + html into
evidence/final_outputs). The fresh payload is gated (row-floor + collapse guard) and the
outputs are size-checked; on ANY failure the last-good outputs are restored and an alert
is written — the portal row is never refreshed with a bad build.
"""
import os, sys, json, shutil, subprocess, datetime, hashlib, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
SQL  = os.path.join(PROJ, "sql", "REQ-25_slow-moving-products")
OUT  = os.path.join(PROJ, "evidence", "final_outputs", "REQ-25_slow-moving-products")
BUILD = os.path.join(SQL, "build_smp_d01.py")
PUBLISH = os.path.join(HERE, "publish_smp_ph_task.py")
PAYLOAD = os.path.join(SQL, "smp_payload.json")
XLSX = os.path.join(OUT, "REQ-25-D01_slow_moving_products.xlsx")
HTML = os.path.join(OUT, "REQ-25-D01_slow_moving_products.html")
STATUS = os.path.join(HERE, "smp_status.txt")
LASTGOOD = os.path.join(HERE, "smp_last_good.json")
ALERT = os.path.join(os.path.expanduser("~"), "Desktop", "SMP_ALERT.txt")

PH_TASK_ID = "735"              # the published portal row to refresh
TABS = ("shopify", "amazon", "ebay", "combined")
FLOORS = {"shopify": 50, "amazon": 50, "ebay": 50, "combined": 500}
COLLAPSE_FRAC = 0.60           # fail if a tab's fresh count < 60% of last-good

def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"; print(line)
    with open(STATUS, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def alert(msg):
    with open(ALERT, "w", encoding="utf-8") as f:
        f.write(f"SMP monthly refresh FAILED {datetime.datetime.now():%Y-%m-%d %H:%M}\n{msg}\n"
                f"Outputs restored to last-good; portal row {PH_TASK_ID} NOT refreshed. See {STATUS}\n")
    log("ALERT: " + msg)

def _lastgood_counts():
    if not os.path.exists(LASTGOOD): return {}
    return json.load(open(LASTGOOD, encoding="utf-8")).get("counts", {})

def main():
    log("=== SMP monthly refresh start ===")
    for v in ("LED_PGHOST", "LED_PGUSER", "LED_PGPASSWORD"):
        if not os.environ.get(v):
            alert(f"missing credential env var {v}"); return 1

    # back up last-good outputs so a bad build can be rolled back
    bak = {}
    for p in (XLSX, HTML):
        if os.path.exists(p):
            bak[p] = p + ".bak"; shutil.copyfile(p, bak[p])

    def restore():
        for p, b in bak.items():
            if os.path.exists(b): shutil.copyfile(b, p)

    # 1. rebuild (fetch RAW mcp.ledsone -> payload + xlsx + html)
    try:
        r = subprocess.run([sys.executable, BUILD], cwd=SQL, capture_output=True, text=True, timeout=900)
        if r.returncode != 0:
            restore(); alert(f"build failed: {r.stderr.strip()[:500]}"); return 1
        log("build: " + (r.stdout.strip().splitlines() or ["(no output)"])[0])
    except Exception as e:
        restore(); alert(f"build crashed: {e}"); return 1

    # 2. gate the fresh payload
    try:
        meta = json.load(open(PAYLOAD, encoding="utf-8"))["meta"]; counts = meta["rows"]
    except Exception as e:
        restore(); alert(f"cannot read payload: {e}"); return 1
    log("row counts: " + json.dumps(counts))
    for t in TABS:
        if counts.get(t, 0) < FLOORS[t]:
            restore(); alert(f"row-floor gate: {t} has {counts.get(t,0)} < {FLOORS[t]}"); return 1
    prev = _lastgood_counts()
    for t in TABS:
        if prev.get(t, 0) and counts[t] < COLLAPSE_FRAC * prev[t]:
            restore(); alert(f"collapse gate: {t} {counts[t]} < {COLLAPSE_FRAC:.0%} of last-good {prev[t]}"); return 1

    # 3. size-check outputs
    for p, floor in ((XLSX, 50000), (HTML, 100000)):
        if not os.path.exists(p) or os.path.getsize(p) < floor:
            restore(); alert(f"output too small/missing: {os.path.basename(p)}"); return 1
    md5 = {os.path.basename(p): hashlib.md5(open(p, "rb").read()).hexdigest() for p in (XLSX, HTML)}

    json.dump({"counts": counts, "md5": md5, "at": f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}"},
              open(LASTGOOD, "w", encoding="utf-8"))

    # 4. refresh the published portal row (only if publish creds present)
    if os.environ.get("PGPASSWORD"):
        try:
            r = subprocess.run([sys.executable, PUBLISH, "--update", PH_TASK_ID],
                               cwd=HERE, capture_output=True, text=True, timeout=180)
            if r.returncode != 0:
                alert(f"portal refresh failed (build OK): {r.stderr.strip()[:400]}"); return 1
            log(f"portal ph_task id {PH_TASK_ID} refreshed (--update).")
        except Exception as e:
            alert(f"portal refresh crashed (build OK): {e}"); return 1
    else:
        log("PGPASSWORD not set — skipped portal refresh (outputs refreshed only).")

    for b in bak.values():                       # clean up backups on success
        if os.path.exists(b): os.remove(b)
    if os.path.exists(ALERT): os.remove(ALERT)
    log(f"OK — {counts} for window ending {meta['win_end']} (html md5 "
        f"{md5['REQ-25-D01_slow_moving_products.html'][:8]}).")
    log("=== SMP monthly refresh done ===")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception:
        tb = traceback.format_exc()
        alert("SMP monthly crashed — see smp_status.txt\n" + tb.splitlines()[-1])
        log("CRASH:\n" + tb); sys.exit(1)
