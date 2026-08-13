# -*- coding: utf-8 -*-
"""
Merge monthly run — self-contained, fleet-pattern automation for the eBay unified dashboard.

Pulls FRESH data by REUSING each source task's own build functions (read-only, NO publish),
writes ONLY into merged_dashboards/ (the 3 task folders are never touched), then runs the
emitters + build_merged.py. Fail-closed: on any gate failure NOTHING is overwritten.

  python merge_monthly_run.py            # real run
  python merge_monthly_run.py --dry-run  # pull + build into a temp dir, write nothing final

Credentials (env only): the source build modules read the same DB env the fleet already sets
(PGHOST/PGPASSWORD warehouse, LED_PGHOST/LED_PGPASSWORD ledsone). No secrets in this file.

STATUS 2026-08-13: EPPR + ESNM refresh LIVE (their build_records / fetch+assemble are clean).
ERA's live data is not cleanly tabular from its build, so v1 carries ERA's LAST-GOOD merge file
and logs it — ERA-live is a flagged follow-up. All three still render; only ERA may lag.
"""
import os, sys, json, time, shutil, tempfile, hashlib, logging, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
MERGE_DIR = os.path.abspath(os.path.join(HERE, ".."))          # merged_dashboards/
EMIT_DIR = os.path.join(MERGE_DIR, "emitters")
PROJECTS = os.path.abspath(os.path.join(MERGE_DIR, "..", "projects"))
STATUS = os.path.join(HERE, "merge_status.txt")
LOG = os.path.join(HERE, "merge_run.log")
DRY = "--dry-run" in sys.argv

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-7s %(message)s")
log = logging.getLogger("merge").info

# source module dirs
EPPR_SQL = os.path.join(PROJECTS, "PRJ-2026-016_ebay-product-performance-analysis", "sql", "REQ-19_ebay-product-performance-analysis")
ESNM_SQL = os.path.join(PROJECTS, "PRJ-2026-014_ebay-slow-no-moving-products", "sql", "REQ-16_ebay-slow-no-moving-products")

MIN_EPPR, MIN_ESNM = 5000, 5000     # floors: real pulls are ~11k each

def die(msg):
    logging.getLogger("merge").error("ABORT: %s", msg)
    with open(STATUS, "w", encoding="utf-8") as f:
        f.write("FAIL %s\n%s\nOutputs NOT changed.\n" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), msg))
    try:
        alert = os.path.join(os.path.expanduser("~"), "Desktop", "MERGE_ALERT.txt")
        with open(alert, "w", encoding="utf-8") as f:
            f.write("Merge dashboard refresh FAILED %s\n%s\n" % (datetime.datetime.now(), msg))
    except Exception:
        pass
    sys.exit(1)

def month_end_before(d):
    first = d.replace(day=1)
    return first - datetime.timedelta(days=1)

# ------------------------------------------------------------------ EPPR (live)
def refresh_eppr(workdir):
    sys.path.insert(0, EPPR_SQL)
    import render_eppr_dashboard as R
    R.JSON_OUT = os.path.join(workdir, "eppr_d01_data.json")   # redirect writes into our workdir
    R.HTML_OUT = os.path.join(workdir, "_eppr_throwaway.html")
    log("EPPR: pulling live via build_records()…")
    R.main()                                                   # writes fresh json to workdir (no publish)
    n = len(json.load(open(R.JSON_OUT, encoding="utf-8"))["records"])
    if n < MIN_EPPR:
        die("EPPR live pull returned %d rows (< floor %d)" % (n, MIN_EPPR))
    log("EPPR: %d rows" % n)
    return R.JSON_OUT

# ------------------------------------------------------------------ ESNM (live)
def refresh_esnm(workdir):
    sys.path.insert(0, ESNM_SQL)
    import build_esnm_d01 as B
    import render_esnm_dashboard as R
    R.OUT_JSON = os.path.join(workdir, "esnm_d01_data.json")   # redirect ALL writes into our workdir
    R.OUT_HTML = os.path.join(workdir, "_esnm_throwaway.html") # (was leaking into the ESNM task folder)
    B.OUT_XLSX = os.path.join(workdir, "_esnm_throwaway.xlsx")
    anchor = month_end_before(datetime.date.today())
    B.set_anchor(anchor); R.B = B
    log("ESNM: pulling live via fetch()/assemble() (anchor %s)…" % anchor)
    data = None
    for attempt in (1, 2, 3):
        try:
            data = B.fetch(); break
        except Exception as e:
            log("  ESNM fetch attempt %d failed: %s" % (attempt, str(e).splitlines()[0]))
            if attempt == 3:
                die("ESNM: all 3 fetch attempts failed")
            time.sleep(15 * attempt)
    rows = B.assemble(data)
    if len(rows) < MIN_ESNM:
        die("ESNM live pull returned %d rows (< floor %d)" % (len(rows), MIN_ESNM))
    R.main(rows, data["cov"])                                  # writes fresh json to workdir (no publish)
    log("ESNM: %d rows" % len(rows))
    return R.OUT_JSON

# ------------------------------------------------------------------ run one emitter with a source override
def run_emitter(script, src_env, src_path):
    import subprocess
    env = dict(os.environ); env[src_env] = src_path
    r = subprocess.run([sys.executable, os.path.join(EMIT_DIR, script)],
                       cwd=EMIT_DIR, env=env, capture_output=True, text=True)
    if r.returncode != 0:
        die("emitter %s failed: %s" % (script, (r.stderr or r.stdout)[-400:]))
    log("emitter %s ok: %s" % (script, (r.stdout or "").strip().splitlines()[-1] if r.stdout else ""))

def main():
    log("=== merge monthly run start (dry_run=%s) ===" % DRY)
    work = tempfile.mkdtemp(prefix="merge_")
    try:
        eppr_json = refresh_eppr(work)
        esnm_json = refresh_esnm(work)

        # emit standard files from the FRESH live sources
        run_emitter("eppr_emit.py", "EPPR_SRC", eppr_json)
        run_emitter("esnm_emit.py", "ESNM_SRC", esnm_json)

        if DRY:
            log("DRY-RUN: fresh emitters written; skipping build_merged/HTML publish.")
            with open(STATUS, "w", encoding="utf-8") as f:
                f.write("OK(dry-run) %s\n" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
            return 0

        import subprocess
        r = subprocess.run([sys.executable, os.path.join(MERGE_DIR, "build_merged.py")],
                           cwd=MERGE_DIR, capture_output=True, text=True)
        if r.returncode != 0:
            die("build_merged failed: %s" % (r.stderr or r.stdout)[-400:])
        html = os.path.join(MERGE_DIR, "ebay_listings_eppr_esnm", "merged_eppr_esnm_dashboard.html")
        if not os.path.exists(html) or os.path.getsize(html) < 1_000_000:
            die("built HTML missing or too small")
        md5 = hashlib.md5(open(html, "rb").read()).hexdigest()[:10]

        # refresh the portal rows in place (only if publish creds present)
        if os.environ.get("PGPASSWORD"):
            r = subprocess.run([sys.executable, os.path.join(HERE, "publish_merge_ph_task.py"), "--refresh"],
                               cwd=HERE, capture_output=True, text=True)
            if r.returncode != 0:
                die("portal refresh failed (build OK): %s" % (r.stderr or r.stdout)[-300:])
            log("portal rows refreshed: " + (r.stdout or "").strip().splitlines()[-1])
        else:
            log("PGPASSWORD not set — built HTML only, skipped portal refresh")

        with open(STATUS, "w", encoding="utf-8") as f:
            f.write("OK %s | html %d bytes | md5 %s\n" %
                    (datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), os.path.getsize(html), md5))
        log("=== merge monthly run done | md5 %s ===" % md5)
        return 0
    finally:
        shutil.rmtree(work, ignore_errors=True)

if __name__ == "__main__":
    sys.exit(main())
