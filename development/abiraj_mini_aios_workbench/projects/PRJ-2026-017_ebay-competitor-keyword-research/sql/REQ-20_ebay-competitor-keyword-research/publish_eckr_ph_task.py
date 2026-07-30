"""
Publish eCKR (REQ-20-D01) — eBay Competitor & Keyword Research — to
tech_team_outputs.ph_task for the ebay_priors team (one row per user).

SAFE BY DEFAULT: dry-run prints exactly what WOULD be written and does NOT
touch the database. Add --commit to actually write.

Guards (learned the hard way on this table):
  * Live table has an 18th column `assigned_user_team` the sample DDL omits -> we SET it ('ebay_priors').
  * The DDL's UNIQUE(task_id) does NOT exist in live -> we SELECT-check each task_id by hand
    and UPDATE if it already exists (never blind-insert a duplicate).
  * Never set id / created_at / updated_at (auto).
  * Read back length(html_content) after writing to prove the payload landed.
  * Retry with backoff on transient "too many clients already".

Credential: password comes from env PGPASSWORD (do NOT hardcode in git).
  set  PGPASSWORD=...   before running with --commit.
Run:  python publish_eckr_ph_task.py            (dry-run)
      python publish_eckr_ph_task.py --commit   (writes)
"""
import os, sys, time

DB = dict(host=os.getenv("PGHOST","149.28.134.54"), port=os.getenv("PGPORT","5435"),
          dbname=os.getenv("PGDATABASE","order_management_copy"),
          user=os.getenv("PGUSER","temp_user"), password=os.getenv("PGPASSWORD",""))

HTML_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
    "..","..","evidence","final_outputs","REQ-20_ebay-competitor-keyword-research","REQ-20-D01_ph_task.html")

USERS = ["Thinesh","Jarsini","kobiga","powsteena"]      # ebay_priors team, exact staff.users.username casing

PROJECT_NAME = ("eckr — eBay Competitor & Keyword Research (top-5 sold-proven eBay UK competitors "
                "+ keyword sets per product across 9 categories) — LEDsONE analytics platform")
PROJECT_CODE = "eckr"
TASK_NAME    = ("eBay Competitor & Keyword Research — 9 product categories, top-5 sold-proven "
                "competitors each (product image, price, feedback %, shipping, promotion) + "
                "generated primary/secondary/long-tail keywords")
DESCRIPTION  = ("Live eBay UK competitor & keyword research for Jarsini's 9 product categories "
                "(Metal Shade Pendant, Wall Light, Metal shade Ceiling, Glass shade, Spider, Cage, "
                "Pipe, Bulbs, Lamp Holder). 42 sold-proven competitors with our own 13 eBay accounts "
                "excluded; each row shows the competitor's product image, price, seller feedback, "
                "shipping (free/paid) and promotion, plus generated keyword sets. Snapshot 2026-07-30.")
TEAM, DEVELOPER, TEAM_TAG = "Development", "Abiraj", "ebay_priors"
PHASE_LEVEL, VERSION_LEVEL, VERSION_STATUS = 1, 1, "released"

def task_id(user): return f"eckr_{user}_ebay_competitor_keyword"

def rows(html):
    for u in USERS:
        yield dict(task_id=task_id(u), assigned_user=u, project_name=PROJECT_NAME,
                   project_code=PROJECT_CODE, task_name=TASK_NAME, description=DESCRIPTION,
                   team=TEAM, developer=DEVELOPER, assigned_user_team=TEAM_TAG,
                   phase_level=PHASE_LEVEL, version_level=VERSION_LEVEL,
                   version_status=VERSION_STATUS, html=html)

def main():
    commit = "--commit" in sys.argv
    with open(HTML_FILE, encoding="utf-8") as f: html = f.read()
    print(f"HTML payload: {len(html):,} chars  ({HTML_FILE})")
    print(f"Mode: {'COMMIT (writing)' if commit else 'DRY-RUN (no DB writes)'}\n")
    print(f"{'task_id':52} {'assigned_user':12} {'team_tag':12} {'status':9} html_len")
    for r in rows(html):
        print(f"{r['task_id']:52} {r['assigned_user']:12} {r['assigned_user_team']:12} {r['version_status']:9} {len(r['html']):,}")

    if not commit:
        print("\nDry-run only. Re-run with --commit (and PGPASSWORD set) to publish these 4 rows.")
        return

    import psycopg2
    if not DB["password"]:
        sys.exit("PGPASSWORD not set — refusing to connect.")
    for attempt in range(5):
        try:
            conn = psycopg2.connect(**DB); break
        except psycopg2.OperationalError as e:
            if "too many clients" in str(e).lower() and attempt < 4:
                print("  transient pool error, retrying…"); time.sleep(2*(attempt+1)); continue
            raise
    try:
        with conn:
            with conn.cursor() as cur:
                for r in rows(html):
                    cur.execute("SELECT id FROM tech_team_outputs.ph_task WHERE task_id=%s", (r["task_id"],))
                    hit = cur.fetchone()
                    if hit:   # guarded UPDATE (preserve user action columns)
                        cur.execute("""UPDATE tech_team_outputs.ph_task
                            SET html_content=%s, project_name=%s, project_code=%s, task_name=%s,
                                description=%s, team=%s, developer=%s, assigned_user=%s,
                                assigned_user_team=%s, phase_level=%s, version_level=%s,
                                version_status=%s, updated_at=now()
                            WHERE id=%s""",
                            (r["html"],r["project_name"],r["project_code"],r["task_name"],r["description"],
                             r["team"],r["developer"],r["assigned_user"],r["assigned_user_team"],
                             r["phase_level"],r["version_level"],r["version_status"],hit[0]))
                        print(f"  UPDATED id={hit[0]}  {r['task_id']}")
                    else:     # INSERT (id/created_at/updated_at auto)
                        cur.execute("""INSERT INTO tech_team_outputs.ph_task
                            (project_name,project_code,task_name,task_id,team,developer,assigned_user,
                             assigned_user_team,html_content,description,phase_level,version_level,version_status)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                            (r["project_name"],r["project_code"],r["task_name"],r["task_id"],r["team"],
                             r["developer"],r["assigned_user"],r["assigned_user_team"],r["html"],
                             r["description"],r["phase_level"],r["version_level"],r["version_status"]))
                        print(f"  INSERTED id={cur.fetchone()[0]}  {r['task_id']}")
        # read-back verify
        with conn.cursor() as cur:
            print("\nRead-back:")
            for r in rows(html):
                cur.execute("SELECT id, assigned_user, assigned_user_team, length(html_content) "
                            "FROM tech_team_outputs.ph_task WHERE task_id=%s", (r["task_id"],))
                print("  ", cur.fetchone(), "expected_len", len(r["html"]))
    finally:
        conn.close()

if __name__ == "__main__":
    main()
