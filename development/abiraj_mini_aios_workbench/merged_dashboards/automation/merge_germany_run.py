# -*- coding: utf-8 -*-
"""
Germany Products merge — live monthly run (FMP + SMP, Mahima).
Runs each task's OWN build (live DB pull, NO publish) to produce a fresh xlsx, reads it via
the emitters, builds the dashboard, and republishes the germany rows. The two builds write into
their task folders; this runner git-restores them afterwards so the task folders end unchanged
(in the cloud the checkout is ephemeral so this is a no-op).

  python merge_germany_run.py            # real run
  python merge_germany_run.py --dry-run  # build fresh data + dashboard, skip publish
"""
import os, sys, json, subprocess, tempfile, hashlib, logging, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
MERGE_DIR = os.path.abspath(os.path.join(HERE, ".."))
EMIT_DIR = os.path.join(MERGE_DIR, "emitters")
PROJECTS = os.path.abspath(os.path.join(MERGE_DIR, "..", "projects"))
STATUS = os.path.join(HERE, "merge_germany_status.txt")
DRY = "--dry-run" in sys.argv
logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-7s %(message)s")
log = logging.getLogger("merge-de").info

FMP_PROJ = os.path.join(PROJECTS, "PRJ-2026-020_fast-moving-products")
FMP_RUN_DIR = os.path.join(FMP_PROJ, "automation")            # fmp_weekly_run.py = live pipeline, no publish
FMP_XLSX = os.path.join(FMP_PROJ, "evidence", "final_outputs", "REQ-23_fast-moving-products",
                        "REQ-23-D01_fast_moving_products.xlsx")
SMP_PROJ = os.path.join(PROJECTS, "PRJ-2026-022_slow-moving-products")
SMP_DIR = os.path.join(SMP_PROJ, "sql", "REQ-25_slow-moving-products")  # build_smp_d01.py = live fetch()+build
SMP_XLSX = os.path.join(SMP_PROJ, "evidence", "final_outputs", "REQ-25_slow-moving-products",
                        "REQ-25-D01_slow_moving_products.xlsx")
MIN_FMP, MIN_SMP = 40, 3000

def die(msg):
    logging.getLogger("merge-de").error("ABORT: %s", msg)
    with open(STATUS, "w", encoding="utf-8") as f:
        f.write("FAIL %s\n%s\n" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), msg))
    sys.exit(1)

def run_build(name, script_dir, script):
    import time
    for attempt in (1, 2, 3):                      # ledsone pool blips intermittently -> retry
        log("%s: running its live build (%s), attempt %d…" % (name, script, attempt))
        r = subprocess.run([sys.executable, os.path.join(script_dir, script)],
                           cwd=script_dir, capture_output=True, text=True)
        if r.returncode == 0:
            return
        log("  %s attempt %d failed: %s" % (name, attempt, (r.stderr or r.stdout).strip()[-200:]))
        if attempt < 3:
            time.sleep(20 * attempt)
    die("%s build failed after 3 attempts" % name)

def run_emitter(script, src_env, src_path):
    env = dict(os.environ); env[src_env] = src_path
    r = subprocess.run([sys.executable, os.path.join(EMIT_DIR, script)],
                       cwd=EMIT_DIR, env=env, capture_output=True, text=True)
    if r.returncode != 0:
        die("emitter %s failed: %s" % (script, (r.stderr or r.stdout)[-400:]))
    log("emitter %s ok: %s" % (script, (r.stdout or "").strip().splitlines()[-1] if r.stdout else ""))
    return json.load(open(os.path.join(EMIT_DIR, script.replace("_emit.py", "_merge.json")), encoding="utf-8"))

def restore(proj_dirs):
    # leave the task folders as they were (best effort; no-op in an ephemeral cloud checkout)
    for d in proj_dirs:
        try:
            subprocess.run(["git", "checkout", "--", d], cwd=PROJECTS, capture_output=True, text=True)
        except Exception:
            pass

def main():
    log("=== germany merge run start (dry_run=%s) ===" % DRY)
    try:
        run_build("FMP", FMP_RUN_DIR, "fmp_weekly_run.py")     # live fetch->build->refresh, no publish
        run_build("SMP", SMP_DIR, "build_smp_d01.py")          # live fetch()+build, no publish

        fmp = run_emitter("fmp_emit.py", "FMP_SRC", FMP_XLSX)
        smp = run_emitter("smp_emit.py", "SMP_SRC", SMP_XLSX)
        if len(fmp["rows"]) < MIN_FMP:
            die("FMP only %d rows (< %d)" % (len(fmp["rows"]), MIN_FMP))
        if len(smp["rows"]) < MIN_SMP:
            die("SMP only %d rows (< %d)" % (len(smp["rows"]), MIN_SMP))
        log("fresh data: FMP %d · SMP %d" % (len(fmp["rows"]), len(smp["rows"])))
    finally:
        restore([FMP_PROJ, SMP_PROJ])

    r = subprocess.run([sys.executable, os.path.join(MERGE_DIR, "build_merged.py"),
                        os.path.join(MERGE_DIR, "registry_germany.json")],
                       cwd=MERGE_DIR, capture_output=True, text=True)
    if r.returncode != 0:
        die("build_merged failed: %s" % (r.stderr or r.stdout)[-400:])
    html = os.path.join(MERGE_DIR, "germany_products_fmp_smp", "merged_germany_products_dashboard.html")
    if not os.path.exists(html) or os.path.getsize(html) < 300_000:
        die("built HTML missing or too small")
    md5 = hashlib.md5(open(html, "rb").read()).hexdigest()[:10]

    if DRY:
        log("DRY-RUN: dashboard built (md5 %s), skipped publish." % md5)
    elif os.environ.get("PGPASSWORD"):
        pub = subprocess.run([sys.executable, os.path.join(HERE, "publish_germany_ph_task.py"), "--refresh"],
                             cwd=HERE, capture_output=True, text=True)
        if pub.returncode != 0:
            die("portal refresh failed (build OK): %s" % (pub.stderr or pub.stdout)[-300:])
        log("portal rows refreshed: " + (pub.stdout or "").strip().splitlines()[-1])
    with open(STATUS, "w", encoding="utf-8") as f:
        f.write("OK%s %s | md5 %s\n" % ("(dry-run)" if DRY else "",
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), md5))
    log("=== germany merge run done | md5 %s ===" % md5)
    return 0

if __name__ == "__main__":
    sys.exit(main())
