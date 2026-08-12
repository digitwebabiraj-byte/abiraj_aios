#!/usr/bin/env python3
"""
Publish REQ-26-D01 (eBay UK Top 50 Sales Drop, esdt) HTML dashboard to the PH portal
table  tech_team_outputs.ph_task  (portal DB order_management_copy @ temp_user).

Modelled on the owner-supplied `temp_user 1.py` sample. Read-only everywhere except the
single guarded write to ph_task. Every insert is verified by an md5 read-back.

Usage:
  # preview only — no write:
  python publish_esdt_ph_task.py --dry-run
  # insert new rows (one per audience user) and verify:
  python publish_esdt_ph_task.py
  # re-publish / refresh an existing row by id:
  python publish_esdt_ph_task.py --update 861

Credentials come from env (PGHOST/PGPORT/PGDATABASE/PGUSER/PGPASSWORD) or fall back to the
sample defaults. Nothing is committed to git.
"""
import os, sys, argparse, hashlib
import psycopg2

DB_CONFIG = {
    "host":     os.getenv("PGHOST", "149.28.134.54"),
    "port":     os.getenv("PGPORT", "5435"),
    "dbname":   os.getenv("PGDATABASE", "order_management_copy"),
    "user":     os.getenv("PGUSER", "temp_user"),
    "password": os.getenv("PGPASSWORD", ""),   # from env / git-ignored esdt_secrets.bat — NEVER hardcode
}


def _require_creds():
    if not DB_CONFIG["password"]:
        raise SystemExit("PGPASSWORD not set — run `esdt_secrets.bat` first (see esdt_secrets.template.bat).")

HERE = os.path.dirname(os.path.abspath(__file__))
HTML_FILE = os.path.normpath(os.path.join(
    HERE, "..", "evidence", "final_outputs", "REQ-26_ebay-top50-sales-drop",
    "REQ-26-D01_ebay_top50_sales_drop.html"))

PROJECT_NAME = "eBay UK Top 50 Sales Drop"
PROJECT_CODE = "esdt"
TASK_NAME    = "REQ-26-D01 — ELECTRICALSONE (30d vs prev 30d)"
DESCRIPTION  = ("Top 50 ELECTRICALSONE eBay-UK SKUs by absolute £ sales loss vs the previous "
                "30-day window, with CTR / CVR / ROAS / stock diagnostics, a priority band and "
                "a recommended action per SKU. Live raw-ledsone data; draft pending Kobiga sign-off.")
DEVELOPER    = "Abiraj"
TEAM         = "Development"
ASSIGNED_USER_TEAM = "ebay_priors"   # portal filters on this; matches epns/eppr/ERA/ebpd/dst/esnm/epc

# Audience — one ph_task row per user (unique task_id each). Kobiga is the requester/account owner.
# Override with --users a,b,c
AUDIENCE_DEFAULT = ["kobiga"]
AUDIENCE_EBAY_TEAM = ["kobiga", "Jarsini", "powsteena", "Thinesh", "Sharmilan", "Sivajitha"]


def read_html():
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        return f.read()


def md5(s):
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def task_id_for(user):
    return f"esdt_{user}_ebay_top50_sales_drop"


def insert_rows(users, dry):
    html = read_html()
    print(f"HTML: {HTML_FILE}\n  size={len(html):,} chars  md5={md5(html)}")
    print(f"Target: {DB_CONFIG['dbname']} @ {DB_CONFIG['host']}:{DB_CONFIG['port']}  ->  tech_team_outputs.ph_task")
    print(f"Rows to INSERT ({len(users)}): team='{TEAM}' developer='{DEVELOPER}' status='released'")
    for u in users:
        print(f"   • assigned_user={u:12s}  task_id={task_id_for(u)}")
    if dry:
        print("\n[dry-run] no write performed."); return

    _require_creds()
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn:
            with conn.cursor() as cur:
                for u in users:
                    tid = task_id_for(u)
                    cur.execute(
                        """
                        INSERT INTO tech_team_outputs.ph_task
                            (project_name, project_code, task_name, task_id, team, developer,
                             assigned_user, assigned_user_team, html_content, description,
                             phase_level, version_level, version_status)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        RETURNING id
                        """,
                        (PROJECT_NAME, PROJECT_CODE, TASK_NAME, tid, TEAM, DEVELOPER,
                         u, ASSIGNED_USER_TEAM, html, DESCRIPTION, 1, 1, "released"),
                    )
                    new_id = cur.fetchone()[0]
                    cur.execute("SELECT md5(html_content) FROM tech_team_outputs.ph_task WHERE id=%s", (new_id,))
                    db_md5 = cur.fetchone()[0]
                    ok = "OK" if db_md5 == md5(html) else "MISMATCH!"
                    print(f"   inserted id={new_id}  user={u}  read-back md5 {ok}")
    finally:
        conn.close()
    print("Done.")


def update_row(row_id, dry):
    html = read_html()
    print(f"HTML: {HTML_FILE}  size={len(html):,}  md5={md5(html)}")
    print(f"UPDATE ph_task id={row_id}  (html_content + updated_at)")
    if dry:
        print("[dry-run] no write performed."); return
    _require_creds()
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE tech_team_outputs.ph_task SET html_content=%s, updated_at=now() WHERE id=%s",
                    (html, row_id))
                print(f"Rows updated: {cur.rowcount}")
                cur.execute("SELECT md5(html_content) FROM tech_team_outputs.ph_task WHERE id=%s", (row_id,))
                r = cur.fetchone()
                print("read-back md5", "OK" if r and r[0] == md5(html) else "MISMATCH!")
    finally:
        conn.close()


def refresh_all(dry):
    """Update html_content of EVERY existing esdt row (used by the monthly automation)."""
    html = read_html(); m = md5(html)
    print(f"HTML: {HTML_FILE}  size={len(html):,}  md5={m}")
    print("REFRESH: update html_content of all rows WHERE project_code='esdt'")
    if dry:
        print("[dry-run] no write performed."); return
    _require_creds()
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE tech_team_outputs.ph_task SET html_content=%s, updated_at=now() "
                            "WHERE project_code=%s", (html, PROJECT_CODE))
                print("rows updated:", cur.rowcount)
                cur.execute("SELECT bool_and(md5(html_content)=%s) FROM tech_team_outputs.ph_task "
                            "WHERE project_code=%s", (m, PROJECT_CODE))
                ok = cur.fetchone()[0]
                print("all rows md5", "OK" if ok else "MISMATCH!")
                if not ok:
                    raise SystemExit("md5 mismatch after refresh")
    finally:
        conn.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--update", type=int, metavar="ID", help="update an existing row id instead of inserting")
    ap.add_argument("--refresh", action="store_true", help="update html_content of ALL esdt rows (automation)")
    ap.add_argument("--users", type=str, help="comma-separated assigned_user list (default: kobiga)")
    ap.add_argument("--ebay-team", action="store_true", help="publish to all eBay PH users")
    a = ap.parse_args()
    if a.refresh:
        refresh_all(a.dry_run)
    elif a.update:
        update_row(a.update, a.dry_run)
    else:
        users = (a.users.split(",") if a.users else
                 (AUDIENCE_EBAY_TEAM if a.ebay_team else AUDIENCE_DEFAULT))
        insert_rows([u.strip() for u in users], a.dry_run)
