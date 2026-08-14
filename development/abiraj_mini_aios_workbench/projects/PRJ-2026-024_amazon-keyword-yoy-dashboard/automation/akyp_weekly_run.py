#!/usr/bin/env python3
"""
REQ-28-D02 — Amazon PPC Keyword YoY, autonomous weekly refresh (every Friday).

Rebuilds the Amazon keyword YoY deliverable live from the ledsone DB (read-only, direct psycopg2 —
a Scheduled Task has no MCP session), then rebuilds and REPUBLISHES Meshika's single merged
"Advertising Dashboards" ph_task row (Amazon tab + eBay tab). The eBay tab reads eppa's current
deliverable, refreshed by the eBay pause automation's own weekly run.

FAILS CLOSED. If the Amazon pull returns too few keyword rows, the existing outputs and the live
ph_task row are left untouched and the status file records the failure — a stale-but-correct page
beats a fresh wrong one.

Credentials: LED_* (ledsone, read data) + PG* (portal, publish) from akyp_secrets.bat (git-ignored).
"""
import os, sys, json, runpy, traceback
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, ".."))
SQLDIR = os.path.join(PROJ, "sql", "REQ-28_amazon-keyword-yoy-dashboard")
PAYLOAD = os.path.join(SQLDIR, "akyp_payload.json")
MERGE_PUB = os.path.abspath(os.path.join(
    PROJ, "..", "..", "merged_dashboards", "ledsone_ppc_meshika", "automation"))
STATUS = os.path.join(HERE, "akyp_status.json")
LOG = os.path.join(HERE, "akyp_run.log")

MIN_KEYWORDS = 200      # fail-closed floor: fewer than this across all markets means a broken pull
PUBLISH = not ("--dry-run" in sys.argv or "--no-publish" in sys.argv)


def log(msg):
    line = "%s  %s" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg)
    print(line, flush=True)
    try:
        with open(LOG, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
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


def main():
    for var in ("LED_PGHOST", "LED_PGDATABASE", "LED_PGUSER", "LED_PGPASSWORD"):
        if not os.environ.get(var):
            raise RuntimeError("missing credential env var %s — is akyp_secrets.bat filled in?" % var)

    # 1) refresh the Amazon deliverable (build payload -> render dashboard)
    runpy.run_path(os.path.join(SQLDIR, "build_akyp_d01.py"), run_name="__main__")
    payload = json.load(open(PAYLOAD, encoding="utf-8"))
    total_kw = sum(len(m["keywords"]) for m in payload["markets"].values())
    if total_kw < MIN_KEYWORDS:
        raise RuntimeError("only %d keyword rows returned (floor %d) — refusing to overwrite"
                           % (total_kw, MIN_KEYWORDS))
    runpy.run_path(os.path.join(SQLDIR, "render_akyp_dashboard.py"), run_name="__main__")
    log("Amazon deliverable refreshed — %d keyword rows across %d markets"
        % (total_kw, len(payload["markets"])))

    # 2) rebuild + republish the merged page (Meshika's single row)
    published = None
    if not PUBLISH:
        log("--dry-run: Amazon files rebuilt; merged page NOT published")
    elif os.environ.get("PGPASSWORD"):
        sys.path.insert(0, MERGE_PUB)
        from publish_merged_meshika import publish   # noqa: E402
        published = publish(commit=True, quiet=True)
        if published:
            log("merged page published to ph_task id=%d version=%d md5=%s"
                % (published["ph_task_id"], published["version_level"], published["html_md5"]))
    else:
        log("WARN: PGPASSWORD not set — Amazon files rebuilt but merged page NOT published")

    st = dict(keyword_rows=total_kw, markets=len(payload["markets"]),
              reference=payload.get("referenceDate"))
    if published:
        st.update(published)
    write_status(True, "refresh ok", st)
    log("REFRESH OK")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        log("FAILED — %s" % exc)
        log(traceback.format_exc())
        write_status(False, str(exc))
        sys.exit(1)
