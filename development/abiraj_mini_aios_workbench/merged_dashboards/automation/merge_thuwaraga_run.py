# -*- coding: utf-8 -*-
"""
Thuwaraga Products merge — live run (T7 + SMAW), IFRAME-EMBED model.
Each tab embeds the task's OWN full dashboard HTML verbatim (its exact columns/values/layout),
so it is byte-identical to the standalone report — nothing is recomputed. Fresh data comes from
running each task's own build with --dry-run (renders its dashboard HTML, publishes nothing):
  • T7   -> t7_weekly_run.py --dry-run     writes automation/t7_auto_dashboard.html
  • SMAW -> smaw_weekly_run.py --dry-run   writes automation/smaw_dashboard.html
Those two dashboards are copied read-only into thuwaraga_t7_smaw/sources/, wrapped in the tabbed
iframe shell, and republished to Thuwaraga. Task folders are restored via git checkout (net-zero).

  python merge_thuwaraga_run.py            # real run
  python merge_thuwaraga_run.py --dry-run  # build the merged page, skip publish
"""
import os, sys, shutil, subprocess, hashlib, logging, datetime, time

HERE = os.path.dirname(os.path.abspath(__file__))
MERGE_DIR = os.path.abspath(os.path.join(HERE, ".."))
PROJECTS = os.path.abspath(os.path.join(MERGE_DIR, "..", "projects"))
SOURCES = os.path.join(MERGE_DIR, "thuwaraga_t7_smaw", "sources")
STATUS = os.path.join(HERE, "merge_thuwaraga_status.txt")
DRY = "--dry-run" in sys.argv
logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-7s %(message)s")
log = logging.getLogger("merge-thu").info

T7_PROJ = os.path.join(PROJECTS, "PRJ-2026-005_weekly-sku-performance-check")
T7_RUN = os.path.join(T7_PROJ, "automation", "t7_weekly_run.py")
T7_HTML = os.path.join(T7_PROJ, "automation", "t7_auto_dashboard.html")
SMAW_PROJ = os.path.join(PROJECTS, "PRJ-2026-004_smaw-table5-stock-check")
SMAW_RUN = os.path.join(SMAW_PROJ, "automation", "smaw_weekly_run.py")
SMAW_HTML = os.path.join(SMAW_PROJ, "automation", "smaw_dashboard.html")


def die(msg):
    logging.getLogger("merge-thu").error("ABORT: %s", msg)
    with open(STATUS, "w", encoding="utf-8") as f:
        f.write("FAIL %s\n%s\n" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), msg))
    sys.exit(1)


def run_task(name, script, out_html):
    d = os.path.dirname(script)
    for attempt in (1, 2, 3):
        log("%s: rendering its own dashboard (--dry-run, attempt %d)…" % (name, attempt))
        r = subprocess.run([sys.executable, script, "--dry-run"], cwd=d, capture_output=True, text=True)
        if r.returncode == 0 and os.path.exists(out_html) and os.path.getsize(out_html) > 100_000:
            return
        log("  %s attempt %d failed: %s" % (name, attempt, (r.stderr or r.stdout).strip()[-260:]))
        if attempt < 3:
            time.sleep(20 * attempt)
    die("%s dashboard build failed after 3 attempts" % name)


def restore(dirs):
    for d in dirs:
        try:
            subprocess.run(["git", "checkout", "--", d], cwd=PROJECTS, capture_output=True, text=True)
        except Exception:
            pass


def main():
    log("=== thuwaraga merge run start (dry_run=%s) ===" % DRY)
    os.makedirs(SOURCES, exist_ok=True)
    try:
        run_task("T7", T7_RUN, T7_HTML)
        run_task("SMAW", SMAW_RUN, SMAW_HTML)
        shutil.copyfile(T7_HTML, os.path.join(SOURCES, "t7_dashboard.html"))
        shutil.copyfile(SMAW_HTML, os.path.join(SOURCES, "smaw_dashboard.html"))
        log("captured both task dashboards: T7 %d B · SMAW %d B"
            % (os.path.getsize(T7_HTML), os.path.getsize(SMAW_HTML)))
    finally:
        restore([T7_PROJ, SMAW_PROJ])

    r = subprocess.run([sys.executable, os.path.join(MERGE_DIR, "build_merged_iframe.py"),
                        os.path.join(MERGE_DIR, "registry_thuwaraga_iframe.json")],
                       cwd=MERGE_DIR, capture_output=True, text=True)
    if r.returncode != 0:
        die("build_merged_iframe failed: %s" % (r.stderr or r.stdout)[-400:])
    html = os.path.join(MERGE_DIR, "thuwaraga_t7_smaw", "merged_thuwaraga_dashboard.html")
    if not os.path.exists(html) or os.path.getsize(html) < 200_000:
        die("built merged HTML missing or too small")
    md5 = hashlib.md5(open(html, "rb").read()).hexdigest()[:10]

    if DRY:
        log("DRY-RUN: merged page built (md5 %s), skipped publish." % md5)
    elif os.environ.get("PGPASSWORD"):
        pub = subprocess.run([sys.executable, os.path.join(HERE, "publish_thuwaraga_ph_task.py"), "--refresh"],
                             cwd=HERE, capture_output=True, text=True)
        if pub.returncode != 0:
            die("portal refresh failed (build OK): %s" % (pub.stderr or pub.stdout)[-300:])
        log("portal rows refreshed: " + (pub.stdout or "").strip().splitlines()[-1])
    with open(STATUS, "w", encoding="utf-8") as f:
        f.write("OK%s %s | md5 %s\n" % ("(dry-run)" if DRY else "",
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), md5))
    log("=== thuwaraga merge run done | md5 %s ===" % md5)
    return 0


if __name__ == "__main__":
    sys.exit(main())
