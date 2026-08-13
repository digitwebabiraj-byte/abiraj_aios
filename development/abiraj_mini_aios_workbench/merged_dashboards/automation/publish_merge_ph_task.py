# -*- coding: utf-8 -*-
"""
Publish the eBay unified (merged) dashboard to tech_team_outputs.ph_task.
One guarded row per eBay PH user, stable task_id (upsert-in-place via --refresh), md5 read-back.
Credentials from env (PGHOST/PGPORT/PGDATABASE/PGUSER/PGPASSWORD).

  python publish_merge_ph_task.py --dry-run          # show plan, write nothing
  python publish_merge_ph_task.py --ebay-team        # INSERT one row per eBay PH user (first time)
  python publish_merge_ph_task.py --refresh          # UPDATE html of all elud rows (automation)
"""
import os, sys, argparse, hashlib, psycopg2

HERE = os.path.dirname(os.path.abspath(__file__))
HTML_FILE = os.path.normpath(os.path.join(HERE, "..", "ebay_listings_eppr_esnm", "merged_eppr_esnm_dashboard.html"))

DB_CONFIG = {
    "host":     os.getenv("PGHOST", "149.28.134.54"),
    "port":     os.getenv("PGPORT", "5435"),
    "dbname":   os.getenv("PGDATABASE", "order_management_copy"),
    "user":     os.getenv("PGUSER", "temp_user"),
    "password": os.getenv("PGPASSWORD"),
}

PROJECT_NAME = "eBay Listings — Unified Dashboard"
PROJECT_CODE = "elud"
TASK_NAME    = "eBay Listings — Unified (Performance + Slow/No-Moving)"
DESCRIPTION  = ("One page combining two eBay per-listing reports — Product Performance (EPPR) and "
                "Slow / No-Moving (ESNM). Pick a task tab to see that task's own listings; search, "
                "sort and filter within each. Refreshes live monthly. A combined VIEW of the two "
                "existing reports — no new data.")
DEVELOPER          = "Abiraj"
TEAM               = "Development"
ASSIGNED_USER_TEAM = "ebay_priors"
AUDIENCE_EBAY_TEAM = ["kobiga", "Jarsini", "powsteena", "Thinesh", "Sharmilan", "Sivajitha"]

def read_html():
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        return f.read()

def md5(s):
    return hashlib.md5(s.encode("utf-8")).hexdigest()

def task_id_for(user):
    return f"elud_{user}_ebay_listings_unified"

def _require_creds():
    if not DB_CONFIG["password"]:
        sys.exit("ABORT: PGPASSWORD not set")

def insert_rows(users, dry):
    html = read_html()
    print(f"Target: {DB_CONFIG['dbname']} @ {DB_CONFIG['host']}  ->  tech_team_outputs.ph_task")
    print(f"INSERT {len(users)} rows · team='{TEAM}' · html {len(html):,} chars · md5 {md5(html)}")
    for u in users:
        print(f"   • assigned_user={u:12s} task_id={task_id_for(u)}")
    if dry:
        print("DRY-RUN: nothing written."); return
    _require_creds()
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn, conn.cursor() as cur:
            for u in users:
                cur.execute(
                    """INSERT INTO tech_team_outputs.ph_task
                       (project_name, project_code, task_name, task_id, team, developer,
                        assigned_user, assigned_user_team, html_content, description,
                        phase_level, version_level, version_status)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                    (PROJECT_NAME, PROJECT_CODE, TASK_NAME, task_id_for(u), TEAM, DEVELOPER,
                     u, ASSIGNED_USER_TEAM, html, DESCRIPTION, 1, 1, "released"))
                nid = cur.fetchone()[0]
                cur.execute("SELECT md5(html_content) FROM tech_team_outputs.ph_task WHERE id=%s", (nid,))
                ok = "OK" if cur.fetchone()[0] == md5(html) else "MISMATCH!"
                print(f"   inserted id={nid} user={u} read-back {ok}")
    finally:
        conn.close()

def refresh_all(dry):
    html = read_html()
    print(f"REFRESH all project_code='{PROJECT_CODE}' rows · html {len(html):,} chars · md5 {md5(html)}")
    if dry:
        print("DRY-RUN: nothing written."); return
    _require_creds()
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn, conn.cursor() as cur:
            cur.execute("UPDATE tech_team_outputs.ph_task SET html_content=%s, updated_at=now() "
                        "WHERE project_code=%s", (html, PROJECT_CODE))
            n = cur.rowcount
            cur.execute("SELECT bool_and(md5(html_content)=%s) FROM tech_team_outputs.ph_task "
                        "WHERE project_code=%s", (md5(html), PROJECT_CODE))
            ok = "OK" if cur.fetchone()[0] else "MISMATCH!"
            print(f"   updated {n} rows · read-back {ok}")
    finally:
        conn.close()

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--ebay-team", action="store_true", help="INSERT one row per eBay PH user")
    ap.add_argument("--refresh", action="store_true", help="UPDATE html of all elud rows")
    a = ap.parse_args()
    if a.refresh:
        refresh_all(a.dry_run)
    else:
        insert_rows(AUDIENCE_EBAY_TEAM, a.dry_run)
