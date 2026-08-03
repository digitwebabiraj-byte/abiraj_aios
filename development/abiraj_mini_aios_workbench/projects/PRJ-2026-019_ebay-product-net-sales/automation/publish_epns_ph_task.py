#!/usr/bin/env python3
"""
publish_epns_ph_task.py — publish REQ-22-D01 eBay Product Net Sales dashboard to
tech_team_outputs.ph_task for the ebay_priors audience (6 users).

GUARDED upsert: SELECT by task_id, then UPDATE (bump version) or INSERT. Idempotent & re-runnable.
Credentials come from env (PGHOST/PGPORT/PGDATABASE/PGUSER/PGPASSWORD) — never hard-coded here.
Dry-run by default; set EPNS_COMMIT=1 to actually write.

Requires: pip install psycopg2-binary
"""
import os, sys, psycopg2

DB = {
    "host":     os.getenv("PGHOST", "149.28.134.54"),
    "port":     os.getenv("PGPORT", "5435"),
    "dbname":   os.getenv("PGDATABASE", "order_management_copy"),
    "user":     os.getenv("PGUSER", "temp_user"),
    "password": os.environ.get("PGPASSWORD"),   # must be supplied via env
}
COMMIT = os.getenv("EPNS_COMMIT") == "1"

HTML_FILE = os.getenv("EPNS_HTML", os.path.join(
    os.path.dirname(__file__), "..", "evidence", "final_outputs",
    "REQ-22_ebay-product-net-sales", "REQ-22-D01_dashboard.html"))

AUDIENCE = ["Thinesh", "Jarsini", "kobiga", "powsteena", "Sharmilan", "Sivajitha"]  # ebay_priors
ASSIGNED_TEAM = "ebay_priors"   # ⚠ the portal ("Ebay Priors") filters on this column — MUST be set,
                                #   or the rows are invisible in the portal (the sample DDL omits it)

PROJECT_NAME = "eBay Product Net Sales"
PROJECT_CODE = "epns"
TASK_NAME    = "REQ-22-D01 eBay Product Net Sales — per-order Net Sales (NNV), settled orders, last 30 days (12 cols)"
TEAM         = "Development"
DEVELOPER    = "Abiraj"
DESCRIPTION  = ("Per-eBay-order Net Sales (NNV) for the last 30 days, SETTLED orders only (fees booked, "
                "ties to eBay's VAT-inclusive fee totals). Net Sales (NNV) = Gross - Final Value Fee - PPC - General. "
                "VAT (20%) and Product Cost (20% proxy) are estimates; Net Profit [est] derives from them. "
                "Built read-only from raw ledsone (source_id=2). Money per marketplace currency, never blended.")

def task_id_for(user): return f"epns_{user}_ebay_product_net_sales"

def main():
    if not DB["password"]:
        sys.exit("PGPASSWORD not set — refusing to run. Provide it via env for this run only.")
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html = f.read()
    print(f"HTML: {os.path.abspath(HTML_FILE)}  ({len(html):,} chars)")
    print(f"Mode: {'COMMIT' if COMMIT else 'DRY-RUN (no write)'}\nAudience: {', '.join(AUDIENCE)}\n")

    conn = psycopg2.connect(**DB); conn.autocommit = False
    try:
        with conn.cursor() as cur:
            for user in AUDIENCE:
                tid = task_id_for(user)
                cur.execute("SELECT id, version_level FROM tech_team_outputs.ph_task WHERE task_id=%s", (tid,))
                row = cur.fetchone()
                if row:
                    rid, ver = row
                    print(f"  UPDATE id={rid:<5} {tid}  (v{ver} -> v{(ver or 0)+1})")
                    if COMMIT:
                        cur.execute("""UPDATE tech_team_outputs.ph_task
                            SET html_content=%s, description=%s, task_name=%s, project_name=%s,
                                developer=%s, assigned_user_team=%s,
                                version_level=COALESCE(version_level,0)+1,
                                version_status='released', updated_at=now()
                            WHERE id=%s""",
                            (html, DESCRIPTION, TASK_NAME, PROJECT_NAME, DEVELOPER, ASSIGNED_TEAM, rid))
                else:
                    print(f"  INSERT new    {tid}  (assigned_user={user})")
                    if COMMIT:
                        cur.execute("""INSERT INTO tech_team_outputs.ph_task
                            (project_name, project_code, task_name, task_id, team, developer,
                             assigned_user, assigned_user_team, html_content, description,
                             phase_level, version_level, version_status)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,1,1,'released')""",
                            (PROJECT_NAME, PROJECT_CODE, TASK_NAME, tid, TEAM, DEVELOPER, user,
                             ASSIGNED_TEAM, html, DESCRIPTION))
        if COMMIT:
            conn.commit(); print("\nCOMMITTED.")
        else:
            conn.rollback(); print("\n(dry-run) rolled back — nothing written. Set EPNS_COMMIT=1 to publish.")
    except Exception as e:
        conn.rollback(); print("ERROR, rolled back:", e); raise
    finally:
        conn.close()

if __name__ == "__main__":
    main()
