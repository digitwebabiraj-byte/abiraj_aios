#!/usr/bin/env python3
"""
Meshika merged dashboard — self-contained refresh + publish (fleet cloud pattern).

Pulls BOTH tabs FRESH by reusing each source task's own build (read-only, no separate publish),
rebuilds the merged page, and refreshes Meshika's single ph_task row. This is the form the cloud
needs: one job, no shared filesystem assumed — each run refreshes Amazon AND eBay before it
publishes (unlike the PC tasks, which each feed the merge from shared local files).

  Amazon (akyp): sql/REQ-28_.../build_akyp_d01.py + render_akyp_dashboard.py
  eBay   (eppa): automation/eppa_weekly_run.py --no-publish  (its own live pull + render + gates)
  then          publish_merged_meshika.publish(commit=True)

FAILS CLOSED. If either source refresh errors (or the eppa gates trip), it raises before the
publish, so the live merged row keeps its last-good version.

  python meshika_merge_run.py             # real run (refresh both + publish)
  python meshika_merge_run.py --dry-run   # refresh both + rebuild, but DO NOT publish

Credentials (env only): LED_* (ledsone read) + PG* (portal publish) — same as the fleet.
"""
import os, sys, json, subprocess, traceback
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
MERGE_DIR = os.path.abspath(os.path.join(HERE, ".."))                     # ledsone_ppc_meshika/
PROJECTS = os.path.abspath(os.path.join(HERE, "..", "..", "..", "projects"))  # workbench/projects/
AKYP_SQL = os.path.join(PROJECTS, "PRJ-2026-024_amazon-keyword-yoy-dashboard",
                        "sql", "REQ-28_amazon-keyword-yoy-dashboard")
AKYP_PAYLOAD = os.path.join(AKYP_SQL, "akyp_payload.json")
EPPA_AUTO = os.path.join(PROJECTS, "PRJ-2026-013_ebay-ppc-product-pause-automation", "automation")
STATUS = os.path.join(HERE, "meshika_merge_status.json")
LOG = os.path.join(HERE, "meshika_merge_run.log")

MIN_KEYWORDS = 200
DRY = "--dry-run" in sys.argv


def log(msg):
    line = "%s  %s" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg)
    print(line, flush=True)
    try:
        open(LOG, "a", encoding="utf-8").write(line + "\n")
    except Exception:
        pass


def write_status(ok, msg, extra=None):
    st = dict(ok=ok, message=msg, when=datetime.now(timezone.utc).isoformat(timespec="seconds"))
    if extra:
        st.update(extra)
    try:
        json.dump(st, open(STATUS, "w", encoding="utf-8"), indent=1)
    except Exception:
        pass


def run(script, *args, cwd=None):
    cmd = [sys.executable, script, *args]
    log("run: %s" % " ".join(os.path.basename(x) for x in cmd))
    r = subprocess.run(cmd, cwd=cwd or os.path.dirname(script), env=os.environ.copy())
    if r.returncode != 0:
        raise RuntimeError("%s exited %d" % (os.path.basename(script), r.returncode))


def main():
    for var in ("LED_PGHOST", "LED_PGDATABASE", "LED_PGUSER", "LED_PGPASSWORD"):
        if not os.environ.get(var):
            raise RuntimeError("missing credential env var %s" % var)

    # 1) refresh the Amazon tab (live) + fail-closed floor
    run(os.path.join(AKYP_SQL, "build_akyp_d01.py"))
    payload = json.load(open(AKYP_PAYLOAD, encoding="utf-8"))
    total_kw = sum(len(m["keywords"]) for m in payload["markets"].values())
    if total_kw < MIN_KEYWORDS:
        raise RuntimeError("Amazon pull returned %d keyword rows (floor %d)" % (total_kw, MIN_KEYWORDS))
    run(os.path.join(AKYP_SQL, "render_akyp_dashboard.py"))
    log("Amazon tab refreshed — %d keyword rows" % total_kw)

    # 2) refresh the eBay tab (live) via eppa's own runner, WITHOUT its publish (its gates apply)
    run(os.path.join(EPPA_AUTO, "eppa_weekly_run.py"), "--no-publish")
    log("eBay tab refreshed via eppa_weekly_run --no-publish")

    # 3) rebuild + publish the merged row (unless dry-run)
    published = None
    if DRY:
        sys.path.insert(0, HERE)
        from publish_merged_meshika import publish   # noqa: E402
        publish(commit=False)
        log("--dry-run: both tabs refreshed, merged rebuilt, NOT published")
    elif os.environ.get("PGPASSWORD"):
        sys.path.insert(0, HERE)
        from publish_merged_meshika import publish   # noqa: E402
        published = publish(commit=True, quiet=True)
        if published:
            log("merged page published to ph_task id=%d version=%d md5=%s"
                % (published["ph_task_id"], published["version_level"], published["html_md5"]))
    else:
        raise RuntimeError("PGPASSWORD not set — refuse to finish without publishing")

    st = dict(keyword_rows=total_kw, markets=len(payload["markets"]))
    if published:
        st.update(published)
    write_status(True, "refresh ok", st)
    log("MESHIKA MERGE OK")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        log("FAILED — %s" % exc)
        log(traceback.format_exc())
        write_status(False, str(exc))
        sys.exit(1)
