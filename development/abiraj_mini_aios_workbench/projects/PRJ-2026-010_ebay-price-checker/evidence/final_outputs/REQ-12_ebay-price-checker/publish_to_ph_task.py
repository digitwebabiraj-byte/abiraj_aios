# -*- coding: utf-8 -*-
"""REQ-12-D01 -> tech_team_outputs.ph_task : guarded single-row INSERT as temp_user.
Dry-run (rollback) first, then real COMMIT. Manual duplicate guard (no UNIQUE on task_id in live)."""
import os, io, sys, psycopg2

# Credentials come from environment variables ONLY — never hardcode/commit the password.
# Set before running:  PGHOST PGPORT PGDATABASE PGUSER PGPASSWORD
CFG = {"host": os.getenv("PGHOST"), "port": os.getenv("PGPORT","5435"),
       "dbname": os.getenv("PGDATABASE","order_management_copy"),
       "user": os.getenv("PGUSER","temp_user"), "password": os.getenv("PGPASSWORD"),
       "connect_timeout": 15}
if not CFG["host"] or not CFG["password"]:
    raise SystemExit("Set PGHOST and PGPASSWORD env vars before running (credentials are not stored in this file).")

HTML_PATH = r"C:/Users/digit/OneDrive/Desktop/DigitWeb_Works_Abiraj/16_07_2026/2026-07-16_abiraj_REQ-epc_REQ-12-D01_price-checker_dashboard.html"

ROW = {
 "project_name": "eBay Price Checker — Amazon-first cross-channel price drift (Amazon ⇄ Website ⇄ eBay), UK & Germany, 13 eBay accounts — LEDsONE analytics platform",
 "project_code": "epc",
 "task_name": "REQ-12-D01 eBay Price Checker — UK & DE price-drift report (126,070 live listings, 13 accounts)",
 "task_id": "epc_Thinesh_ebay_price_checker-V1",
 "team": "Development",
 "developer": "Abiraj",
 "assigned_user": "Thinesh",
 "description": ("eBay Price Checker (REQ-12-D01). Read-only cross-channel price-drift report over 126,070 live eBay UK & DE "
   "listings across Thinesh's 13 accounts. Target = Amazon (amazon Ledsone) price x0.90 [lowest], else website x1.10, "
   "else DATA MISSING; tolerance +/-£0.50/£1.00 at the £20 band. Sources (live, read-only, refreshed 2026-07-15): "
   "listings.ebay_listings / amazon_listings / shopify_listings (ledsone + ledsone-de) on the ledsone DB. SKU-normalised "
   "per AIOS rules (all_list=1, Amazon _-suffix, ENC->sku_original, PK pack qty). Result: Priced OK 21,138 / Too high 40,261 "
   "/ Too low 22,008 / No target 42,663 (21,048 eBay-only + 21,615 bundles). SIGNED OFF 2026-07-16 (CLOSED). "
   "Status is computed on item price only (shipping accepted at sign-off; a shipping-aware refresh = future "
   "REQ-12-D02) - use for ranking, not repricing. Note: this script published the initial Thinesh row; the "
   "fan-out to Jarsini/kobiga/powsteena (ids 299-301) used the same guarded pattern."),
 "phase_level": 1,
 "version_level": 1,
 "version_status": "released",
 "assigned_user_team": "ebay_priors",
}

COLS = ["project_name","project_code","task_name","task_id","team","developer","assigned_user",
        "html_content","description","phase_level","version_level","version_status","assigned_user_team"]

GUARD = "SELECT id, task_id, project_code FROM tech_team_outputs.ph_task WHERE task_id=%s OR project_code=%s"
INSERT = ("INSERT INTO tech_team_outputs.ph_task (" + ",".join(COLS) + ") VALUES (" +
          ",".join(["%s"]*len(COLS)) + ") RETURNING id, created_at")

def main():
    html = io.open(HTML_PATH, "r", encoding="utf-8").read()
    print("html_content bytes:", len(html.encode("utf-8")))
    vals = [ROW["project_name"],ROW["project_code"],ROW["task_name"],ROW["task_id"],ROW["team"],
            ROW["developer"],ROW["assigned_user"],html,ROW["description"],ROW["phase_level"],
            ROW["version_level"],ROW["version_status"],ROW["assigned_user_team"]]

    conn = psycopg2.connect(**CFG); conn.set_client_encoding("UTF8"); conn.autocommit = False
    try:
        # ---------- PHASE 1: DRY RUN (rollback) ----------
        with conn.cursor() as cur:
            cur.execute(GUARD, (ROW["task_id"], ROW["project_code"]))
            dup = cur.fetchall()
            if dup:
                print("ABORT (dry): duplicate already present:", dup); conn.rollback(); return
            cur.execute(INSERT, vals)
            got = cur.fetchone()
            print("DRY RUN ok -> would insert id=%s created_at=%s rowcount=%s" % (got[0], got[1], cur.rowcount))
        conn.rollback()
        print("DRY RUN rolled back - nothing written yet")

        # ---------- PHASE 2: REAL COMMIT ----------
        with conn.cursor() as cur:
            cur.execute(GUARD, (ROW["task_id"], ROW["project_code"]))
            dup = cur.fetchall()
            if dup:
                print("ABORT (commit): duplicate appeared:", dup); conn.rollback(); return
            cur.execute(INSERT, vals)
            new_id, created = cur.fetchone()
            if cur.rowcount != 1:
                print("ABORT: rowcount != 1 (%s)" % cur.rowcount); conn.rollback(); return
        conn.commit()
        print("COMMITTED -> new row id=%s created_at=%s" % (new_id, created))

        # ---------- verify ----------
        with conn.cursor() as cur:
            cur.execute("""SELECT id, project_code, task_id, assigned_user, assigned_user_team, version_status,
                           octet_length(html_content) FROM tech_team_outputs.ph_task WHERE id=%s""", (new_id,))
            print("VERIFY:", cur.fetchone())
    finally:
        conn.close()

if __name__ == "__main__":
    main()
