# -*- coding: utf-8 -*-
"""
Merged — eBay Account Performance (EBPD + DST) · live monthly run.
Reuses each task's OWN live build to pull FRESH data WITHOUT publishing:
  • EBPD — its weekly runner via ebpd_capture.py (--no-publish); captures in-memory ROWS to temp.
  • DST  — its daily runner with --dry-run (writes a fresh dst_d01_data.json, publishes nothing).
Then the emitters -> build_merged.py -> republish the ebay_priors rows. Task folders restored
via git checkout. Both tasks read their own DBs via their own env (EBPD: warehouse PG* + ledsone
LED_*; DST: ledsone LED_*) — separate env vars, so no PGPORT stripping is needed here.

  python merge_ebay_account_run.py            # real run
  python merge_ebay_account_run.py --dry-run  # build fresh data + dashboard, skip publish
"""
import os, sys, json, subprocess, tempfile, hashlib, logging, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
MERGE_DIR = os.path.abspath(os.path.join(HERE, ".."))
EMIT_DIR = os.path.join(MERGE_DIR, "emitters")
PROJECTS = os.path.abspath(os.path.join(MERGE_DIR, "..", "projects"))
STATUS = os.path.join(HERE, "merge_ebay_account_status.txt")
DRY = "--dry-run" in sys.argv
logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-7s %(message)s")
log = logging.getLogger("merge-eacc").info

EBPD_PROJ = os.path.join(PROJECTS, "PRJ-2026-011_ebay-account-performance-dashboard")
EBPD_RUNNER = os.path.join(EBPD_PROJ, "automation", "ebpd_weekly_run.py")
DST_PROJ = os.path.join(PROJECTS, "PRJ-2026-015_daily-sales-track")
DST_RUN_DIR = os.path.join(DST_PROJ, "automation")
import glob as _glob
MIN_EBPD, MIN_DST = 10, 20


def die(msg):
    logging.getLogger("merge-eacc").error("ABORT: %s", msg)
    with open(STATUS, "w", encoding="utf-8") as f:
        f.write("FAIL %s\n%s\n" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), msg))
    sys.exit(1)


def run(name, cmd, cwd, extra_env=None):
    import time
    env = dict(os.environ)
    if extra_env:
        env.update(extra_env)
    for attempt in (1, 2, 3):
        log("%s: live build (attempt %d)…" % (name, attempt))
        r = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)
        if r.returncode == 0:
            return r
        log("  %s attempt %d failed: %s" % (name, attempt, (r.stderr or r.stdout).strip()[-260:]))
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
    for d in proj_dirs:
        try:
            subprocess.run(["git", "checkout", "--", d], cwd=PROJECTS, capture_output=True, text=True)
        except Exception:
            pass


def main():
    log("=== eBay Account merge run start (dry_run=%s) ===" % DRY)
    work = tempfile.mkdtemp(prefix="eacc_")
    try:
        # EBPD: capture fresh ROWS via its own runner (--no-publish), to temp
        ebpd_out = os.path.join(work, "ebpd_rows.json")
        run("EBPD", [sys.executable, os.path.join(HERE, "ebpd_capture.py")], HERE,
            extra_env={"EBPD_RUNNER": EBPD_RUNNER, "EBPD_OUT": ebpd_out})

        # DST: its own daily runner --dry-run writes a fresh dst_d01_data.json (no publish)
        run("DST", [sys.executable, os.path.join(DST_RUN_DIR, "dst_daily_run.py"), "--dry-run"], DST_RUN_DIR)
        dst_json = _glob.glob(os.path.join(DST_PROJ, "**", "dst_d01_data.json"), recursive=True)
        if not dst_json:
            die("DST dst_d01_data.json not found after its dry-run")
        dst_json = max(dst_json, key=os.path.getmtime)

        ebpd = run_emitter("ebpd_emit.py", "EBPD_SRC", ebpd_out)
        dst = run_emitter("dst_emit.py", "DST_SRC", dst_json)
        if len(ebpd["rows"]) < MIN_EBPD:
            die("EBPD only %d rows (< %d)" % (len(ebpd["rows"]), MIN_EBPD))
        if len(dst["rows"]) < MIN_DST:
            die("DST only %d rows (< %d)" % (len(dst["rows"]), MIN_DST))
        log("fresh data: EBPD %d · DST %d" % (len(ebpd["rows"]), len(dst["rows"])))
    finally:
        restore([EBPD_PROJ, DST_PROJ])
        import shutil; shutil.rmtree(work, ignore_errors=True)

    r = subprocess.run([sys.executable, os.path.join(MERGE_DIR, "build_merged.py"),
                        os.path.join(MERGE_DIR, "registry_ebay_account.json")],
                       cwd=MERGE_DIR, capture_output=True, text=True)
    if r.returncode != 0:
        die("build_merged failed: %s" % (r.stderr or r.stdout)[-400:])
    html = os.path.join(MERGE_DIR, "ebay_account_ebpd_dst", "merged_ebay_account_dashboard.html")
    if not os.path.exists(html) or os.path.getsize(html) < 20_000:
        die("built HTML missing or too small")
    md5 = hashlib.md5(open(html, "rb").read()).hexdigest()[:10]

    if DRY:
        log("DRY-RUN: dashboard built (md5 %s), skipped publish." % md5)
    elif os.environ.get("PGPASSWORD"):
        pub = subprocess.run([sys.executable, os.path.join(HERE, "publish_ebay_account_ph_task.py"), "--refresh"],
                             cwd=HERE, capture_output=True, text=True)
        if pub.returncode != 0:
            die("portal refresh failed (build OK): %s" % (pub.stderr or pub.stdout)[-300:])
        log("portal rows refreshed: " + (pub.stdout or "").strip().splitlines()[-1])
    with open(STATUS, "w", encoding="utf-8") as f:
        f.write("OK%s %s | md5 %s\n" % ("(dry-run)" if DRY else "",
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), md5))
    log("=== eBay Account merge run done | md5 %s ===" % md5)
    return 0


if __name__ == "__main__":
    sys.exit(main())
