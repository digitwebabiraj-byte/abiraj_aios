"""
delete_departed.py  —  remove ph_task rows for holders who have LEFT the roster,
                       AFTER backing up each full row (restorable).

Use when the dashboard shows more cards than the current roster (e.g. 2026-07-10:
33 cards -> should be 31; Poovitha #65 + thanucha #79 had left and were deleted).

SAFETY: full-row backup (all columns incl html_content) is written BEFORE the
DELETE, in ONE transaction. To restore, re-INSERT from the JSON backup.

Set PGPASSWORD env var (creds live in Downloads/temp_user 1.py — never commit them).
Edit IDS + BKDIR before running.
"""
import psycopg2, json, os
DB = dict(host="149.28.134.54", port="5435", dbname="order_management_copy",
          user="temp_user", password=os.getenv("PGPASSWORD"))

IDS   = [65, 79]                       # <-- ph_task ids of the departed holders
BKDIR = r"<PROJECT>\evidence\final_outputs\REQ-05_ph-asin-segmentation\<DATE>_deleted_rows_backup"
COLS  = ["id","project_name","project_code","task_name","task_id","team","developer","assigned_user",
         "html_content","description","phase_level","version_level","version_status",
         "action_took_by","action_took_date_time","created_at","updated_at","assigned_user_team"]

os.makedirs(BKDIR, exist_ok=True)
conn = psycopg2.connect(connect_timeout=20, **DB)
try:
    with conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT {','.join(COLS)} FROM tech_team_outputs.ph_task WHERE id = ANY(%s) ORDER BY id",(IDS,))
            rows = cur.fetchall()
            assert len(rows) == len(IDS), f"expected {len(IDS)} rows, got {len(rows)}"
            for r in rows:
                d = {c:(v.isoformat() if hasattr(v,'isoformat') else v) for c,v in zip(COLS,r)}
                json.dump(d, open(os.path.join(BKDIR,f"ph_task_{d['id']}_{d['assigned_user']}.json"),"w",encoding="utf-8"),
                          ensure_ascii=False, indent=1)
                print("backed up", d['id'], d['assigned_user'])
            cur.execute("DELETE FROM tech_team_outputs.ph_task WHERE id = ANY(%s)",(IDS,))
            print("ROWS DELETED:", cur.rowcount)
            assert cur.rowcount == len(IDS)
    print("COMMITTED OK")
finally:
    conn.close()
