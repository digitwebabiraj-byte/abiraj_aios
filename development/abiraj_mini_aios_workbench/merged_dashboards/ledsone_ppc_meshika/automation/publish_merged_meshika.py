#!/usr/bin/env python3
"""
Publish the merged "Meshika — Advertising Dashboards" page to tech_team_outputs.ph_task.

One row for Meshika (task_id="meshika_advertising_dashboards"): the merged page whose two tabs are
the Amazon Keyword YoY dashboard (akyp / PRJ-2026-024) and the eBay PPC Pause dashboard (eppa /
PRJ-2026-013). Rebuilds the merged HTML from the two projects' current deliverables first, then
refreshes the row.

Mirrors the estate publish convention (eppa_publish_ph_task): identity fixed, DELETE-by-task_id +
INSERT in ONE transaction (production has no unique constraint on task_id, so a plain INSERT would
duplicate on every run), md5 read-back verify. Also removes the now-superseded standalone eBay row
(task_id="eppa_meshika_ebay_ppc_pause_dashboard") so Meshika ends with a single merged row.

Read-only by default: prints what it WOULD do. Pass --commit to write. Portal creds come from
PG* env vars (temp_user); never hardcoded.
"""
import os, sys, time, runpy, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
MERGE_DIR = os.path.abspath(os.path.join(HERE, ".."))
BUILDER = os.path.join(MERGE_DIR, "build_merged_meshika.py")
MERGED_HTML = os.path.join(MERGE_DIR, "merged_ledsone_ppc_meshika_dashboard.html")

DB = {
    "host":     os.getenv("PGHOST", "149.28.134.54"),
    "port":     os.getenv("PGPORT", "5435"),
    "dbname":   os.getenv("PGDATABASE", "order_management_copy"),
    "user":     os.getenv("PGUSER", "temp_user"),
    "password": os.getenv("PGPASSWORD"),
}

IDENTITY = dict(
    project_name="Advertising Dashboards — Meshika",
    project_code="meshika_ads",
    task_id="meshika_advertising_dashboards",
    team="Development",
    developer="Abiraj",
    assigned_user="meshika",
    assigned_user_team="cppc_priors",
    phase_level=1,
    version_status="released",
)
TASK_NAME = "Advertising Dashboards — Amazon Keyword YoY + eBay PPC Pause (Meshika)"
DESCRIPTION = (
    "One page combining Meshika's two advertising dashboards, switch by the tabs at the top: "
    "(1) Amazon Ads — Keyword Year-on-Year (amazon Ledsone, UK/US/CA/DE/FR/IT; keyword-level "
    "sales/spend/orders/clicks/impressions vs the same window last year, with per-keyword "
    "diagnosis, priority and recommended action); (2) eBay Ads — Pause Report (LEDSone eBay UK "
    "Promoted Listings pause recommendations). Each tab keeps its own live data and logic; "
    "nothing is recomputed by the merge. Amazon refreshes every Friday; eBay refreshes on the "
    "eBay pause automation's weekly run. Read-only reporting — nothing is paused or changed "
    "automatically.")

# the standalone eBay row this merged page supersedes (removed once so Meshika has one row)
SUPERSEDED_TASK_ID = "eppa_meshika_ebay_ppc_pause_dashboard"


def rebuild():
    runpy.run_path(BUILDER, run_name="__main__")
    with open(MERGED_HTML, "r", encoding="utf-8") as f:
        return f.read()


def connect(attempts=6, first_wait=10):
    import psycopg2
    wait = first_wait
    for i in range(1, attempts + 1):
        try:
            return psycopg2.connect(connect_timeout=20, **DB)
        except psycopg2.OperationalError as exc:
            transient = any(t in str(exc) for t in (
                "remaining connection slots", "too many clients",
                "server closed the connection unexpectedly", "could not connect"))
            if not transient or i == attempts:
                raise
            print("  connect attempt %d/%d failed — retrying in %ds" % (i, attempts, wait), flush=True)
            time.sleep(wait); wait *= 2


COLS = ["project_name", "project_code", "task_name", "task_id", "team", "developer",
        "assigned_user", "assigned_user_team", "html_content", "description",
        "phase_level", "version_level", "version_status"]


def publish(commit=False, quiet=False):
    html = rebuild()
    file_md5 = hashlib.md5(html.encode("utf-8")).hexdigest()
    if not quiet:
        print("merged html: %d bytes  md5=%s" % (len(html), file_md5))
    if not DB["password"]:
        raise RuntimeError("PGPASSWORD not set — cannot reach the portal (fill meshika/publish secrets)")

    conn = connect()
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COALESCE(MAX(version_level),0) FROM tech_team_outputs.ph_task "
                        "WHERE task_id=%s", (IDENTITY["task_id"],))
            next_ver = cur.fetchone()[0] + 1
            cur.execute("SELECT id FROM tech_team_outputs.ph_task WHERE task_id=%s ORDER BY id",
                        (IDENTITY["task_id"],))
            old = [r[0] for r in cur.fetchall()]
            cur.execute("SELECT id FROM tech_team_outputs.ph_task WHERE task_id=%s",
                        (SUPERSEDED_TASK_ID,))
            superseded = [r[0] for r in cur.fetchall()]

            if not commit:
                conn.rollback()
                print("DRY-RUN (no write). Would DELETE merged rows %s + superseded eBay rows %s, "
                      "then INSERT task_id=%s version=%d assigned_user=%s team=%s"
                      % (old or "none", superseded or "none", IDENTITY["task_id"], next_ver,
                         IDENTITY["assigned_user"], IDENTITY["assigned_user_team"]))
                return None

            row = dict(IDENTITY)
            row["task_name"] = TASK_NAME
            row["description"] = DESCRIPTION
            row["html_content"] = html
            row["version_level"] = next_ver
            cur.execute("DELETE FROM tech_team_outputs.ph_task WHERE task_id=%s",
                        (IDENTITY["task_id"],))
            if superseded:
                cur.execute("DELETE FROM tech_team_outputs.ph_task WHERE task_id=%s",
                            (SUPERSEDED_TASK_ID,))
            placeholders = ",".join(["%s"] * len(COLS))
            cur.execute("INSERT INTO tech_team_outputs.ph_task (%s) VALUES (%s) RETURNING id"
                        % (",".join(COLS), placeholders), [row[c] for c in COLS])
            new_id = cur.fetchone()[0]
            cur.execute("SELECT MD5(html_content) FROM tech_team_outputs.ph_task WHERE id=%s", (new_id,))
            db_md5 = cur.fetchone()[0]
        if db_md5 != file_md5:
            conn.rollback()
            raise RuntimeError("md5 mismatch after insert (file %s vs db %s) — rolled back"
                               % (file_md5, db_md5))
        conn.commit()
        print("published id=%d version=%d (replaced %s, removed superseded %s) md5=%s"
              % (new_id, next_ver, old or "none", superseded or "none", db_md5))
        return dict(ph_task_id=new_id, version_level=next_ver, html_md5=db_md5)
    finally:
        conn.close()


if __name__ == "__main__":
    publish(commit=("--commit" in sys.argv))
