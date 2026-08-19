"""
Publish the BGCT Keyword Gap dashboard (REQ-30) to tech_team_outputs.ph_task
for Thuwaraga (audience `ph_priors`).

Guarded INSERT ... RETURNING, then reads the row back and md5-verifies the html landed intact.
Connection = the portal DB `order_management_copy` as temp_user, matching the sample script.
Password comes from env PGPASSWORD only - never hard-coded, never committed.

  set PGPASSWORD=...
  python publish_bgct_ph_task.py --dry-run        # print the row, write nothing
  python publish_bgct_ph_task.py                  # INSERT a new row
  python publish_bgct_ph_task.py --update <id>    # refresh OUR row's html (bumps version_level)

🔴 PROJECT_CODE COLLISION - the reason this uses `bgct-kwgap` and not `bgct`
`tech_team_outputs.ph_task` already holds project_code 'BGCT' at **id 9 = "BGCT Listing Generator"**,
developer tharsika, assigned to **utharsika**, last updated 2026-08-17. That is a different team's
live project that merely shares the BGCT prefix. Publishing under `bgct` would collide with it in the
portal, and updating id 9 would destroy their work. This script therefore uses a distinct
project_code and REFUSES to write to any row it does not own - see guard() below.
"""
import os, sys, hashlib, psycopg2

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DB = dict(
    host=os.getenv("PGHOST", "149.28.134.54"),
    port=os.getenv("PGPORT", "5435"),
    dbname=os.getenv("PGDATABASE", "order_management_copy"),
    user=os.getenv("PGUSER", "temp_user"),
    password=os.getenv("PGPASSWORD", ""),      # env only - never commit the value
    connect_timeout=25,
)

HERE = os.path.dirname(os.path.abspath(__file__))
HTML_PATH = os.path.join(HERE, "..", "evidence", "final_outputs",
                         "REQ-30_amazon-keyword-gap-sync", "REQ-30_bgct_keyword_dashboard.html")

# Conventions read off Thuwaraga's other live rows (SMAW 137, WSPC 135, tpts 950):
#   assigned_user 'thuwaraga' (lowercase) · assigned_user_team 'ph_priors' ·
#   team 'Development' · developer 'Abiraj' · description blank (the portal renders it as a header).
ROW = {
    "project_name": "BGCT Keyword Collection & Cross-ASIN Gap Sync — Amazon UK LED bulbs "
                    "(DCVOLTAGE UK + LEDSone UK) — proven Amazon search terms checked against "
                    "declining and zero-sale listings of the same base SKU",
    "project_code": "bgct-kwgap",
    "task_name": "BGCT Keyword Gap Sync — REQ-30 — Phase 1 proven keywords + Phase 2 gaps to fix",
    "task_id": "bgct-kwgap-2026-08-19-thuwaraga",
    "team": "Development",
    "developer": "Abiraj",
    "assigned_user": "thuwaraga",
    "assigned_user_team": "ph_priors",
    "description": "",
    "phase_level": 1,
    "version_level": 1,
    "version_status": "released",
}

# Any row we may legitimately overwrite must match these. id 9 (BGCT Listing Generator) never will.
OWNED = {"project_code": ROW["project_code"], "task_id": ROW["task_id"]}


def guard(cur, row_id):
    """Refuse to touch a row that is not ours. Protects id 9 and anything else in the table."""
    cur.execute("SELECT id, project_code, task_id, developer, assigned_user "
                "FROM tech_team_outputs.ph_task WHERE id=%s", (row_id,))
    r = cur.fetchone()
    if not r:
        sys.exit(f"REFUSED: no ph_task row with id={row_id}.")
    _, code, tid, dev, user = r
    if code != OWNED["project_code"] or tid != OWNED["task_id"]:
        sys.exit(f"REFUSED: id={row_id} is project_code={code!r} task_id={tid!r} "
                 f"(developer {dev}, assigned to {user}) — that is not this project's row. "
                 f"Expected project_code={OWNED['project_code']!r} task_id={OWNED['task_id']!r}.")
    print(f"guard OK: id={row_id} is ours ({code} / {tid})")


def main():
    if not DB["password"]:
        sys.exit("REFUSED: PGPASSWORD is not set. Set it in the environment; it is never committed.")

    html = open(HTML_PATH, encoding="utf-8").read()
    md5 = hashlib.md5(html.encode()).hexdigest()
    print(f"HTML: {os.path.normpath(HTML_PATH)}\n      {len(html):,} chars, md5 {md5}")

    dry = "--dry-run" in sys.argv
    upd_id = int(sys.argv[sys.argv.index("--update") + 1]) if "--update" in sys.argv else None

    print("\nROW for tech_team_outputs.ph_task:")
    for k, v in ROW.items():
        print(f"  {k:20} = {v}")
    print(f"  {'html_content':20} = <{len(html):,} chars, md5 {md5}>")
    print(f"\nmode: {'UPDATE id=' + str(upd_id) if upd_id else 'INSERT new row'}")
    if dry:
        print("\n[dry-run] nothing written.")
        return

    conn = psycopg2.connect(**DB)
    try:
        with conn:
            with conn.cursor() as cur:
                if upd_id:
                    guard(cur, upd_id)
                    cur.execute("UPDATE tech_team_outputs.ph_task "
                                "SET html_content=%s, task_name=%s, description=%s, "
                                "    version_level=version_level+1, updated_at=now() "
                                "WHERE id=%s",
                                (html, ROW["task_name"], ROW["description"], upd_id))
                    row_id = upd_id
                    print(f"UPDATED id={row_id} (rows: {cur.rowcount})")
                else:
                    cur.execute("SELECT id FROM tech_team_outputs.ph_task WHERE task_id=%s",
                                (ROW["task_id"],))
                    dup = cur.fetchone()
                    if dup:
                        sys.exit(f"REFUSED: task_id {ROW['task_id']!r} already exists at id={dup[0]}. "
                                 f"Use --update {dup[0]} to refresh it.")
                    cols = list(ROW) + ["html_content"]
                    vals = [ROW[k] for k in ROW] + [html]
                    cur.execute(
                        f"INSERT INTO tech_team_outputs.ph_task "
                        f"({', '.join(cols)}, created_at, updated_at) "
                        f"VALUES ({','.join(['%s'] * len(cols))}, now(), now()) RETURNING id", vals)
                    row_id = cur.fetchone()[0]
                    print(f"INSERTED id={row_id}")

                cur.execute("SELECT id, project_code, task_id, assigned_user, assigned_user_team, "
                            "team, developer, version_status, version_level, "
                            "length(html_content), md5(html_content), created_at, updated_at "
                            "FROM tech_team_outputs.ph_task WHERE id=%s", (row_id,))
                r = cur.fetchone()

        keys = ["id", "project_code", "task_id", "assigned_user", "assigned_user_team", "team",
                "developer", "version_status", "version_level", "html_len", "html_md5",
                "created_at", "updated_at"]
        print("\n   READ-BACK:")
        for k, v in zip(keys, r):
            print(f"     {k:20} = {v}")
        ok = r[10] == md5
        print(f"\n   md5 match: {ok}")
        if not ok:
            sys.exit("FAILED: the stored html does not match the file. Investigate before telling "
                     "anyone it is published.")
        print("   the dashboard in the portal is byte-identical to the file on disk.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
