# -*- coding: utf-8 -*-
"""
Publish the Merged — eBay Account Performance dashboard to tech_team_outputs.ph_task.
One guarded row per eBay PH user, stable task_id (upsert via --refresh), md5 read-back.

  python publish_ebay_account_ph_task.py --dry-run
  python publish_ebay_account_ph_task.py --team        # INSERT one row per user
  python publish_ebay_account_ph_task.py --refresh     # UPDATE html+name of all eacc rows (automation)
"""
import os, sys, argparse, hashlib, psycopg2

HERE = os.path.dirname(os.path.abspath(__file__))
HTML_FILE = os.path.normpath(os.path.join(HERE, "..", "ebay_account_ebpd_dst",
                                          "merged_ebay_account_dashboard.html"))
DB_CONFIG = {
    "host":     os.getenv("PGHOST", "149.28.134.54"),
    "port":     os.getenv("PGPORT", "5435"),
    "dbname":   os.getenv("PGDATABASE", "order_management_copy"),
    "user":     os.getenv("PGUSER", "temp_user"),
    "password": os.getenv("PGPASSWORD"),
}
PROJECT_NAME = "Merged — eBay Account Performance"
PROJECT_CODE = "eacc"
TASK_NAME    = "Merged — eBay Account Performance (Account KPIs + Daily Sales)"
DESCRIPTION  = ("One page combining two eBay account×marketplace reports — monthly Account "
                "Performance (EBPD) and Daily Sales Track (DST). Pick a task tab to see that "
                "task's own account rows; search, sort and filter within each. Refreshes live "
                "monthly. A combined VIEW of the two existing reports — no new data.")
DEVELOPER          = "Abiraj"
TEAM               = "Development"
ASSIGNED_USER_TEAM = "ebay_priors"
AUDIENCE = ["kobiga", "Jarsini", "powsteena", "Thinesh", "Sharmilan", "Sivajitha"]

def read_html():
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        return f.read()
def md5(s):
    return hashlib.md5(s.encode("utf-8")).hexdigest()
def task_id_for(user):
    return f"eacc_{user}_ebay_account_performance"
def _require():
    if not DB_CONFIG["password"]:
        sys.exit("ABORT: PGPASSWORD not set")

def insert_rows(users, dry):
    html = read_html()
    print(f"INSERT {len(users)} rows · html {len(html):,} chars · md5 {md5(html)}")
    for u in users:
        print(f"   • assigned_user={u:12s} task_id={task_id_for(u)}")
    if dry:
        print("DRY-RUN: nothing written."); return
    _require()
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
    print(f"REFRESH all project_code='{PROJECT_CODE}' · html {len(html):,} chars · md5 {md5(html)}")
    if dry:
        print("DRY-RUN: nothing written."); return
    _require()
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn, conn.cursor() as cur:
            cur.execute("UPDATE tech_team_outputs.ph_task SET html_content=%s, project_name=%s, "
                        "task_name=%s, description=%s, updated_at=now() WHERE project_code=%s",
                        (html, PROJECT_NAME, TASK_NAME, DESCRIPTION, PROJECT_CODE))
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
    ap.add_argument("--team", action="store_true")
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--users", type=str)
    a = ap.parse_args()
    users = a.users.split(",") if a.users else AUDIENCE
    if a.refresh:
        refresh_all(a.dry_run)
    else:
        insert_rows(users, a.dry_run)
