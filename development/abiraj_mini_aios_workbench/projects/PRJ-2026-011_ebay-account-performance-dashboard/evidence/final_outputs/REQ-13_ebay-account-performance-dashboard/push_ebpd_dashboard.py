"""
Push the eBay Account Performance Dashboard (REQ-13-D01) HTML to the assigned
users by inserting one row per user into tech_team_outputs.ph_task.

Pattern follows yesterday's epc (REQ-12-D01) publish. Idempotent: re-running
UPDATEs the existing row (ON CONFLICT on the unique task_id) instead of erroring.

Requires: pip install psycopg2-binary
"""

import os
import psycopg2
from psycopg2.extras import execute_values

# --- Connection settings (same remote DB as the temp_user sample) ---
DB_CONFIG = {
    "host":     os.getenv("PGHOST", "149.28.134.54"),
    "port":     os.getenv("PGPORT", "5435"),
    "dbname":   os.getenv("PGDATABASE", "order_management_copy"),
    "user":     os.getenv("PGUSER", "temp_user"),
    "password": os.getenv("PGPASSWORD"),  # set PGPASSWORD in your env before running
}

HTML_FILE_PATH = r"C:\Users\digit\Downloads\eBay Account Performance Dashboard - June 2026 - FINAL.html"

PROJECT_NAME = ("eBay Account Performance Dashboard — monthly account KPIs across all eBay "
                "marketplaces (Sales, Advertising, Listings & Stock), 12 active accounts — "
                "LEDsONE analytics platform")
PROJECT_CODE = "ebpd"
TASK_NAME    = "REQ-13-D01 eBay Account Performance Dashboard — June 2026 (12 accounts, all 7 marketplaces)"
TEAM         = "Development"
DEVELOPER    = "Abiraj"
ASSIGNED_USER_TEAM = "ebay_priors"   # team-visibility group — MUST be set (sample DDL omits this column); matches epc publish
DESCRIPTION  = ("eBay Account Performance Dashboard (REQ-13-D01) — June 2026, all 12 active eBay "
                "accounts across 7 marketplaces. Revenue £97,019 (product + postage) · 4,625 orders · "
                "7,330 units · ACOS 13.11% · ROAS 7.63 · 14,288 active listings · 248 new listings. "
                "Sales/Advertising/Listings with MoM & YoY, whole-account conversion, Sales Rank by revenue.")

# The users this eBay dashboard is published to (same as yesterday's epc publish)
ASSIGNED_USERS = ["Thinesh", "Jarsini", "kobiga", "powsteena"]


def main():
    with open(HTML_FILE_PATH, "r", encoding="utf-8") as f:
        html_content = f.read()

    rows = [
        (
            PROJECT_NAME, PROJECT_CODE, TASK_NAME,
            f"ebpd_{user}_ebay_account_performance-V1",   # unique task_id per user
            TEAM, DEVELOPER, user, ASSIGNED_USER_TEAM, html_content, DESCRIPTION,
            1,            # phase_level
            1,            # version_level
            "released",   # version_status
        )
        for user in ASSIGNED_USERS
    ]

    task_ids = [f"ebpd_{u}_ebay_account_performance-V1" for u in ASSIGNED_USERS]

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn:
            with conn.cursor() as cur:
                # idempotent: remove any prior rows for these exact task_ids first
                # (the table has no UNIQUE(task_id) constraint, so ON CONFLICT is unavailable)
                cur.execute(
                    "DELETE FROM tech_team_outputs.ph_task WHERE task_id = ANY(%s)",
                    (task_ids,),
                )
                if cur.rowcount:
                    print(f"  removed {cur.rowcount} pre-existing row(s) for these task_ids")
                execute_values(
                    cur,
                    """
                    INSERT INTO tech_team_outputs.ph_task
                        (project_name, project_code, task_name, task_id, team, developer,
                         assigned_user, assigned_user_team, html_content, description, phase_level,
                         version_level, version_status, created_at, updated_at)
                    VALUES %s
                    RETURNING id, assigned_user, assigned_user_team, task_id
                    """,
                    rows,
                    template="(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),now())",
                )
                for r in cur.fetchall():
                    print(f"  pushed id={r[0]:<4} user={r[1]:<12} team={r[2]:<12} task_id={r[3]}")
                print(f"Total rows pushed: {cur.rowcount}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
