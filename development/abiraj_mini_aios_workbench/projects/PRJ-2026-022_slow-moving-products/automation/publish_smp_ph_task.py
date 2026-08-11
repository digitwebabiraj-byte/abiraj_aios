"""
Publish the Slow Moving Products (REQ-25-D01) dashboard to tech_team_outputs.ph_task
as a NEW row for the `german_priors` audience (same audience as Fast Moving #020, id 673).
Guarded INSERT ... RETURNING, then reads the row back and md5-verifies the html landed intact.

Connection = warehouse `order_management_copy` as temp_user (the portal DB), matching the
sample script. Password via env PGPASSWORD (never hard-coded / committed).

  python publish_smp_ph_task.py --dry-run       # print the row, write nothing
  python publish_smp_ph_task.py                 # INSERT a new row
  python publish_smp_ph_task.py --update <id>   # refresh an existing row (html + task_name)
"""
import os, sys, hashlib, psycopg2
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

DB = dict(
    host=os.getenv("PGHOST", "149.28.134.54"),
    port=os.getenv("PGPORT", "5435"),
    dbname=os.getenv("PGDATABASE", "order_management_copy"),
    user=os.getenv("PGUSER", "temp_user"),
    password=os.getenv("PGPASSWORD", ""),   # set PGPASSWORD in env — never commit the value
    connect_timeout=25,
)

HERE = os.path.dirname(os.path.abspath(__file__))
HTML_PATH = os.path.join(HERE, "..", "evidence", "final_outputs",
                         "REQ-25_slow-moving-products", "REQ-25-D01_slow_moving_products.html")

ROW = {
    "project_name": "Slow Moving Products — Germany (Shopify / Amazon / eBay DE) — stock that isn't selling — LEDsONE analytics platform",
    "project_code": "smp",
    "task_name": "Slow Moving Products (Germany) — REQ-25-D01 — 4 tabs (Shopify / Amazon / eBay DE + Combined)",
    "task_id": "smp-2026-08-11-DE-Mahi",
    "team": "Development",
    "developer": "Abiraj",
    "assigned_user": "Mahima",
    "assigned_user_team": "german_priors",
    "description": "",   # portal shows this as a header block — kept blank, matching Fast Moving
    "phase_level": 1,
    "version_level": 1,
    "version_status": "released",
}

def main():
    dry = "--dry-run" in sys.argv
    html = open(HTML_PATH, encoding="utf-8").read()
    md5 = hashlib.md5(html.encode()).hexdigest()
    print(f"HTML: {HTML_PATH}\n      {len(html):,} chars, md5 {md5}")
    print("\nNEW ROW to insert into tech_team_outputs.ph_task:")
    for k, v in ROW.items():
        print(f"  {k:20} = {v}")
    print(f"  {'html_content':20} = <{len(html):,} chars, md5 {md5}>")
    if dry:
        print("\n[dry-run] nothing written."); return

    upd_id = None
    if "--update" in sys.argv:
        upd_id = int(sys.argv[sys.argv.index("--update") + 1])

    conn = psycopg2.connect(**DB)
    try:
        with conn:
            with conn.cursor() as cur:
                if upd_id:
                    cur.execute("UPDATE tech_team_outputs.ph_task "
                                "SET html_content=%s, description=%s, task_name=%s, version_level=version_level+1, "
                                "updated_at=now() WHERE id=%s",
                                (html, ROW["description"], ROW["task_name"], upd_id))
                    row_id = upd_id
                    print(f"\nUPDATED id={row_id} (rows: {cur.rowcount})")
                else:
                    cols = list(ROW.keys()) + ["html_content"]
                    vals = [ROW[k] for k in ROW] + [html]
                    ph = ",".join(["%s"] * len(cols))
                    cur.execute(f"INSERT INTO tech_team_outputs.ph_task ({', '.join(cols)}, created_at, updated_at) "
                                f"VALUES ({ph}, now(), now()) RETURNING id", vals)
                    row_id = cur.fetchone()[0]
                    print(f"\nINSERTED id={row_id}")
                cur.execute("SELECT id, project_code, task_id, assigned_user, assigned_user_team, team, "
                            "version_status, version_level, length(html_content), md5(html_content), "
                            "coalesce(description,''), created_at FROM tech_team_outputs.ph_task WHERE id=%s", (row_id,))
                r = cur.fetchone()
        keys = ["id","project_code","task_id","assigned_user","assigned_user_team","team","version_status",
                "version_level","html_len","html_md5","description","created_at"]
        print("\n   READ-BACK (the inserted row):")
        for k, v in zip(keys, r):
            print(f"     {k:18} = {v}")
        print("\n   md5 match:", r[9] == md5)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
