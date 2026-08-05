"""
publish_chop_ph_task.py — publish REQ-24-D01 Channel Opportunity dashboard to tech_team_outputs.ph_task.

Adapted from the owner's sample (temp_user). Differences:
  * INSERTs a NEW row (RETURNING id) instead of UPDATEing a fixed id.
  * Matches THIS live schema (team column + UNIQUE(task_id)).
  * Guarded: DRY-RUN by default (read-only) — prints the exact row + live columns and does NOT write.
    Pass --commit to actually INSERT, then it reads the row back and md5-verifies html_content.
  * Password comes from env (PGPASSWORD) only — never hardcoded/committed.

Run:
    python publish_chop_ph_task.py            # dry-run: show the row, no write
    PGPASSWORD=... python publish_chop_ph_task.py --commit   # actually insert
"""
import os, sys, hashlib, psycopg2

DB_CONFIG = {
    "host":     os.getenv("PGHOST", "149.28.134.54"),
    "port":     os.getenv("PGPORT", "5435"),
    "dbname":   os.getenv("PGDATABASE", "order_management_copy"),
    "user":     os.getenv("PGUSER", "temp_user"),
    "password": os.getenv("PGPASSWORD", ""),   # env only — no secret in source
}

HERE = os.path.dirname(os.path.abspath(__file__))
HTML_FILE_PATH = os.path.abspath(os.path.join(
    HERE, "..", "evidence", "final_outputs", "REQ-24_channel-opportunity",
    "REQ-24-D01_channel_opportunity.html"))

# --- the row to publish (all business fields explicit) ---
ROW = {
    "project_name":      "Channel Opportunity",
    "project_code":      "chop",
    "task_name":         "Channel Opportunity — cross-channel listing-gap finder (Shopify/Amazon/eBay, DE)",
    "task_id":           "chop-2026-08-05-DE-Mahi",   # must be UNIQUE(task_id)
    "team":              "Development",                # mirrors fmp id 673
    "assigned_user_team": "german_priors",            # the column the portal actually filters on
    "developer":         "Abiraj",
    "assigned_user":     "Mahi",                       # staff.users id 40 (Mahima)
    "description":       "",                            # blank, as fmp id 673
    "phase_level":       1,
    "version_level":     1,
    "version_status":    "released",
}


def main():
    commit = "--commit" in sys.argv
    with open(HTML_FILE_PATH, "r", encoding="utf-8") as f:
        html = f.read()
    md5 = hashlib.md5(html.encode("utf-8")).hexdigest()

    print("=" * 78)
    print("TARGET  :", f"{DB_CONFIG['user']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/"
          f"{DB_CONFIG['dbname']} → tech_team_outputs.ph_task")
    print("HTML    :", HTML_FILE_PATH)
    print("html len:", f"{len(html):,} chars   md5:", md5)
    print("MODE    :", "COMMIT (will INSERT)" if commit else "DRY-RUN (read-only, no write)")
    print("=" * 78)
    print("ROW TO INSERT:")
    for k, v in ROW.items():
        print(f"  {k:<15}: {v}")
    print(f"  {'html_content':<15}: <{len(html):,} chars, md5 {md5}>")
    print("=" * 78)

    if not DB_CONFIG["password"]:
        print("NOTE: PGPASSWORD not set in env — cannot connect. Set it to run live "
              "(dry-run still needs it to read the live schema).")
        return

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            # live schema check
            cur.execute("""SELECT column_name FROM information_schema.columns
                           WHERE table_schema='tech_team_outputs' AND table_name='ph_task'
                           ORDER BY ordinal_position""")
            cols = [r[0] for r in cur.fetchall()]
            print("LIVE COLUMNS:", ", ".join(cols))
            missing = [k for k in ROW if k not in cols] + (["html_content"] if "html_content" not in cols else [])
            if missing:
                print("!! these fields are NOT in the live table:", missing, "— fix before commit.")
            cur.execute("SELECT COALESCE(MAX(id),0) FROM tech_team_outputs.ph_task")
            print("current MAX(id):", cur.fetchone()[0])
            cur.execute("SELECT id FROM tech_team_outputs.ph_task WHERE task_id=%s", (ROW["task_id"],))
            dup = cur.fetchone()
            print("task_id already exists?:", ("YES id=%s (INSERT would violate UNIQUE)" % dup[0]) if dup else "no")

            if not commit:
                print("\nDRY-RUN complete — nothing written. Re-run with --commit to insert.")
                return

            cols_ins = list(ROW.keys()) + ["html_content"]
            vals = list(ROW.values()) + [html]
            ph = ", ".join(["%s"] * len(cols_ins))
            cur.execute(
                f'INSERT INTO tech_team_outputs.ph_task ({", ".join(cols_ins)}) '
                f'VALUES ({ph}) RETURNING id', vals)
            new_id = cur.fetchone()[0]
            # read back + verify
            cur.execute("SELECT md5(html_content), length(html_content) FROM tech_team_outputs.ph_task WHERE id=%s",
                        (new_id,))
            db_md5, db_len = cur.fetchone()
            conn.commit()
            print(f"\nINSERTED id={new_id}  db_len={db_len:,}  db_md5={db_md5}  "
                  f"{'MATCH ✓' if db_md5 == md5 else 'MISMATCH ✗'}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
