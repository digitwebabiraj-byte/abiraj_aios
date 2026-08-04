#!/usr/bin/env python3
"""
REQ-21-D01 — publish the B2B Session Drop Tracker (Amazon.de) dashboard to the ops portal
tech_team_outputs.ph_task, routed to end user Jensika via assigned_user_team='ah_priors'.

Target DB = the WAREHOUSE order_management_copy (NOT the ledsone raw DB) — ph_task lives there.
Guarded: DRY-RUN by default (prints the exact row, writes nothing). Set PUBLISH=1 to write.
Idempotent: SELECT by task_id → UPDATE if it exists (bump version_level) else INSERT; then read back.
No password in code — supply via env PGPASSWORD.

Requires: pip install psycopg2-binary
"""
import os, sys, hashlib
from pathlib import Path
import psycopg2

HERE = Path(__file__).resolve().parent
PROJ = HERE.parent.parent
HTML = PROJ / "evidence/final_outputs/REQ-21_b2b-session-drop-tracker-de/REQ-21-D01_b2b_session_drop_tracker_DE.html"

DB_CONFIG = {
    "host":     os.getenv("PGHOST", "149.28.134.54"),
    "port":     os.getenv("PGPORT", "5435"),
    "dbname":   os.getenv("PGDATABASE", "order_management_copy"),
    "user":     os.getenv("PGUSER", "temp_user"),
    "password": os.getenv("PGPASSWORD"),   # <-- supply via env, never hardcode
}

# --- the row (one recipient: Jensika, audience ah_priors) ---
ROW = {
    "project_name": "B2B Session Drop Tracker — Germany (Amazon.de) — B2B business-customer traffic decline monitor — LEDsONE analytics platform",
    "project_code": "bsdt",
    "task_name":    "B2B Session Drop Tracker (Amazon.de) — 526 ASINs — data as of 2026-07-15",
    "task_id":      "bsdt-2026-07-15-DE-jensika",
    "team":         "Development",
    "developer":    "Abiraj",
    "assigned_user":      "jensika",
    "assigned_user_team": "ah_priors",
    "description":  ("B2B Session Drop Tracker for Amazon.de (Germany). Source of record = Amazon.de "
                     "Seller Central Business Report export (the internal DB reproduces only ~part of it). "
                     "526 ASINs — Tier 1 Low 506 / Tier 2 Moderate 16 / Tier 3 High 4; 276 with dropped B2B "
                     "sessions. Windows: previous 2026-05-17→2026-06-15, current 2026-06-16→2026-07-15. "
                     "Tier = MAX(prev,current) B2B Sessions (T2≥5, T3≥10). Routed to jensika via "
                     "assigned_user_team='ah_priors'. Read-only."),
    "phase_level":    1,
    "version_level":  1,
    "version_status": "released",
}

def main():
    if not HTML.exists():
        sys.exit(f"HTML not found: {HTML}")
    html = HTML.read_text(encoding="utf-8")
    md5 = hashlib.md5(html.encode("utf-8")).hexdigest()
    publish = os.getenv("PUBLISH") == "1"

    print("=" * 78)
    print("ph_task ROW PREVIEW  (target:", DB_CONFIG["dbname"], "· tech_team_outputs.ph_task)")
    print("=" * 78)
    for k, v in ROW.items():
        print(f"  {k:18}: {v}")
    print(f"  {'html_content':18}: <{len(html):,} chars, md5 {md5}>  ({HTML.name})")
    print("=" * 78)
    print("MODE:", "LIVE PUBLISH" if publish else "DRY-RUN (no write) — set PUBLISH=1 to write")
    if not publish:
        return
    if not DB_CONFIG["password"]:
        sys.exit("Refusing to write: set PGPASSWORD in the environment.")

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, version_level FROM tech_team_outputs.ph_task WHERE task_id=%s",
                            (ROW["task_id"],))
                found = cur.fetchone()
                if found:
                    rid, ver = found
                    cur.execute("""
                        UPDATE tech_team_outputs.ph_task
                           SET project_name=%(project_name)s, project_code=%(project_code)s,
                               task_name=%(task_name)s, team=%(team)s, developer=%(developer)s,
                               assigned_user=%(assigned_user)s, assigned_user_team=%(assigned_user_team)s,
                               html_content=%(html)s, description=%(description)s,
                               phase_level=%(phase_level)s, version_level=%(new_ver)s,
                               version_status=%(version_status)s, updated_at=now()
                         WHERE id=%(id)s
                    """, {**ROW, "html": html, "new_ver": ver + 1, "id": rid})
                    print(f"UPDATED id={rid} (version_level {ver} -> {ver+1})")
                    tid_check = rid
                else:
                    cur.execute("""
                        INSERT INTO tech_team_outputs.ph_task
                            (project_name, project_code, task_name, task_id, team, developer,
                             assigned_user, assigned_user_team, html_content, description,
                             phase_level, version_level, version_status, created_at, updated_at)
                        VALUES
                            (%(project_name)s, %(project_code)s, %(task_name)s, %(task_id)s, %(team)s,
                             %(developer)s, %(assigned_user)s, %(assigned_user_team)s, %(html)s,
                             %(description)s, %(phase_level)s, %(version_level)s, %(version_status)s,
                             now(), now())
                        RETURNING id
                    """, {**ROW, "html": html})
                    tid_check = cur.fetchone()[0]
                    print(f"INSERTED id={tid_check}")
                # read-back verify
                cur.execute("""SELECT id, assigned_user, assigned_user_team, version_level,
                                      md5(html_content), length(html_content)
                               FROM tech_team_outputs.ph_task WHERE id=%s""", (tid_check,))
                rb = cur.fetchone()
                print("READ-BACK:", dict(zip(
                    ["id","assigned_user","assigned_user_team","version_level","md5","html_len"], rb)))
                assert rb[4] == md5, "md5 mismatch after write!"
                print("md5 verified OK.")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
