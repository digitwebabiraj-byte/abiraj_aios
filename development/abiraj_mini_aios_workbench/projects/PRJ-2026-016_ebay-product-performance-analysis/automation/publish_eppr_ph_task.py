# -*- coding: utf-8 -*-
"""
Publish REQ-19-D01 to tech_team_outputs.ph_task for the ebay_priors audience (Thinesh, Jarsini,
kobiga, powsteena) — one row per user, same static HTML.

GUARDED:
  * DRY-RUN by default — prints exactly the rows it WOULD write and touches nothing.
    Run with  --commit  to actually write.
  * Live table has NO working UNIQUE(task_id) (the sample DDL is wrong), so we SELECT-then-
    UPDATE-else-INSERT per task_id inside ONE transaction — never a blind INSERT (which would
    silently duplicate) and never ON CONFLICT (which would error).
  * Sets assigned_user_team (mandatory, and absent from the sample DDL) or rows never reach the audience.
Connection: temp_user @ order_management_copy (the publish account) — same as the sample script.
"""
import os, sys, psycopg2

# Password from the shared global env store (PGPASSWORD) — never hardcoded in tracked code.
DB = {"host": os.getenv("PGHOST","149.28.134.54"), "port": os.getenv("PGPORT","5435"),
      "dbname": os.getenv("PGDATABASE","order_management_copy"),
      "user": os.getenv("PGUSER","temp_user"), "password": os.getenv("PGPASSWORD","")}

HTML_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..","evidence","final_outputs",
      "REQ-19_ebay-product-performance-analysis","REQ-19-D01_ph_task.html"))

RECIPIENTS = ["Thinesh", "Jarsini", "kobiga", "powsteena", "Sharmilan", "Sivajitha"]   # ebay_priors — exact usernames from live rows (Sharmilan+Sivajitha added 2026-07-28)
ROW = dict(project_name="eBay Product Performance Analysis", project_code="eppr",
           task_name="REQ-19-D01 eBay Product Performance Analysis — per-listing, UK+DE (35 cols)",
           team="Development", developer="Abiraj", assigned_user_team="ebay_priors",
           version_status="released", phase_level=1, version_level=1, description=None)

def main(commit):
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html_content = f.read()
    plan = [dict(ROW, assigned_user=u, task_id=f"eppr_{u}_ebay_product_performance") for u in RECIPIENTS]

    print("HTML file: %s  (%.2f MB)" % (HTML_FILE, os.path.getsize(HTML_FILE)/1e6))
    print("Mode: %s\n" % ("COMMIT" if commit else "DRY-RUN (no write)"))
    conn = psycopg2.connect(**DB)
    try:
        with conn:
            with conn.cursor() as cur:
                print("%-11s %-42s %-12s %-4s %s" % ("assigned", "task_id", "team", "ver", "existing_id"))
                for p in plan:
                    cur.execute("SELECT id FROM tech_team_outputs.ph_task WHERE task_id=%s", (p["task_id"],))
                    ex = cur.fetchone()
                    print("%-11s %-42s %-12s %-4s %s" %
                          (p["assigned_user"], p["task_id"], p["assigned_user_team"], p["version_level"],
                           ("UPDATE id=%s" % ex[0]) if ex else "INSERT (new)"))
                if not commit:
                    print("\nDRY-RUN only — nothing written. Re-run with --commit to publish.")
                    conn.rollback(); return
                ids = []
                for p in plan:
                    cur.execute("SELECT id FROM tech_team_outputs.ph_task WHERE task_id=%s", (p["task_id"],))
                    ex = cur.fetchone()
                    if ex:
                        cur.execute("""UPDATE tech_team_outputs.ph_task
                              SET html_content=%s, version_level=version_level+1, version_status=%s, updated_at=now()
                              WHERE id=%s RETURNING id""", (html_content, p["version_status"], ex[0]))
                    else:
                        cur.execute("""INSERT INTO tech_team_outputs.ph_task
                              (project_name,project_code,task_name,task_id,team,developer,assigned_user,
                               assigned_user_team,html_content,description,phase_level,version_level,version_status)
                              VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                              (p["project_name"],p["project_code"],p["task_name"],p["task_id"],p["team"],
                               p["developer"],p["assigned_user"],p["assigned_user_team"],html_content,
                               p["description"],p["phase_level"],p["version_level"],p["version_status"]))
                    ids.append((p["assigned_user"], cur.fetchone()[0]))
                print("\nCOMMITTED rows:", ids)
    finally:
        conn.close()

if __name__ == "__main__":
    main(commit="--commit" in sys.argv)
