import psycopg2, hashlib, os
# Set PGPASSWORD env var before running. temp_user creds are in Downloads/temp_user 1.py — DO NOT commit them.
# EACH CYCLE update: NEW (path to the fresh leader HTML), BACKUP (dated pre-update backup path).
DB=dict(host="149.28.134.54",port="5435",dbname="order_management_copy",user="temp_user",password=os.getenv("PGPASSWORD"))
NEW=r"C:\Users\digit\Downloads\PH_ASIN_Dashboard_ALLPH_corrected_2026-07.html"
TASK_ID=5
BACKUP=r"C:\Users\digit\OneDrive\Desktop\Abiraj_AIOS\.claude\worktrees\phase-asin-segmentation-progress-4a77f8\development\abiraj_mini_aios_workbench\projects\PRJ-2026-001_ph-segmentation\evidence\final_outputs\REQ-05_ph-asin-segmentation\2026-07-10_ph_task_id5_PRE-UPDATE_backup.html"

new_html=open(NEW,encoding="utf-8").read()
new_md5=hashlib.md5(new_html.encode("utf-8")).hexdigest()
print("new file:", len(new_html.encode('utf-8')), "bytes, md5", new_md5)

conn=psycopg2.connect(connect_timeout=20, **DB)
try:
    with conn:
        with conn.cursor() as cur:
            # 1) read + back up current
            cur.execute("SELECT html_content, md5(html_content), length(html_content) FROM tech_team_outputs.ph_task WHERE id=%s", (TASK_ID,))
            row=cur.fetchone()
            assert row is not None, "id=5 not found!"
            cur_html, cur_md5, cur_len = row
            with open(BACKUP,"w",encoding="utf-8",newline="") as f: f.write(cur_html)
            assert os.path.getsize(BACKUP)>0, "backup empty"
            print("BACKED UP current id=5:", cur_len, "chars, md5", cur_md5)
            print("  -> backup:", BACKUP, "(", os.path.getsize(BACKUP), "bytes )")
            # 2) update
            cur.execute("UPDATE tech_team_outputs.ph_task SET html_content=%s, updated_at=now() WHERE id=%s", (new_html, TASK_ID))
            print("ROWS UPDATED:", cur.rowcount)
            assert cur.rowcount==1, "expected exactly 1 row"
            # 3) verify within same transaction (md5 of stored content)
            cur.execute("SELECT md5(html_content), length(html_content), updated_at FROM tech_team_outputs.ph_task WHERE id=%s", (TASK_ID,))
            v_md5, v_len, v_upd = cur.fetchone()
            print("AFTER UPDATE: len", v_len, "md5", v_md5, "updated_at", v_upd)
            assert v_md5==new_md5, f"VERIFY FAILED: stored {v_md5} != expected {new_md5}"
            print("VERIFY: stored md5 == new file md5  -> MATCH")
    print("TRANSACTION COMMITTED OK")
finally:
    conn.close()
