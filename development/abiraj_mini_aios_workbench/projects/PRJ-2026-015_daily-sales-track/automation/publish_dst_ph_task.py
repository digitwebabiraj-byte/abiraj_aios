# -*- coding: utf-8 -*-
"""
Publish REQ-17-D01 (Daily Sales Track dashboard) to tech_team_outputs.ph_task.

DRY-RUN BY DEFAULT. Nothing is written unless you pass --commit.

    python publish_dst_ph_task.py              # preview only
    python publish_dst_ph_task.py --commit     # actually write

CREDENTIALS ARE NEVER STORED HERE. The password is read from the PGPASSWORD
environment variable and there is no default. Set it in the shell for the run:

    set PGPASSWORD=...        (cmd)      or      $env:PGPASSWORD='...'   (PowerShell)

--- Live-schema facts this script relies on (verified 2026-07-23, not assumed) ---

1. `assigned_user_team` EXISTS in live and is REQUIRED for the row to reach an
   audience. It is MISSING from the sample DDL that ships with the example
   script - a row without it is published to nobody.

2. There is NO UNIQUE CONSTRAINT on `task_id`. The sample DDL claims
   `CONSTRAINT ph_task_task_id_unique UNIQUE (task_id)`; live has only
   PRIMARY KEY (id) plus NOT NULLs. So `ON CONFLICT (task_id)` fails, and a
   blind INSERT silently duplicates the report. This script therefore does
   SELECT-then-INSERT-or-UPDATE and refuses to proceed on an ambiguous match.

3. task_id is deliberately STABLE (no date in it). Decision I says this report
   is a snapshot that REPLACES each morning, so tomorrow's run must update the
   same row rather than accumulate one row per day.
"""

import argparse
import io
import os
import sys

import psycopg2

DB = {
    "host": os.getenv("PGHOST", "149.28.134.54"),
    "port": os.getenv("PGPORT", "5435"),
    "dbname": os.getenv("PGDATABASE", "order_management_copy"),
    "user": os.getenv("PGUSER", "temp_user"),
    "password": os.getenv("PGPASSWORD"),  # no default, on purpose
}

HERE = os.path.dirname(os.path.abspath(__file__))
HTML_PATH = os.path.abspath(os.path.join(
    HERE, "..", "evidence", "final_outputs", "REQ-17_daily-sales-track",
    "REQ-17-D01_dst_dashboard.html"))

PROJECT_NAME = "Daily Sales Track"
PROJECT_CODE = "dst"
TASK_NAME = "REQ-17-D01 Daily Sales Track — eBay, account × marketplace (trading day 22 Jul 2026)"
TEAM = "Development"
DEVELOPER = "Abiraj"
AUDIENCE = "ebay_priors"
RECIPIENTS = ["Thinesh", "Jarsini", "kobiga", "powsteena", "Sharmilan", "Sivajitha"]  # ebay_priors — exact live usernames (Sharmilan+Sivajitha added 2026-07-31, same audience as eppr)
VERSION_STATUS = "released"
PHASE_LEVEL = 1
DESCRIPTION = None  # ESNM precedent: the portal renders this above the report and eats ~90px

MIN_HTML_BYTES = 20000  # sanity floor - refuse to publish a truncated build


def task_id_for(user):
    return "{0}_{1}_daily_sales_track".format(PROJECT_CODE, user)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", action="store_true", help="actually write (default is dry-run)")
    args = ap.parse_args()

    if not DB["password"]:
        print("PGPASSWORD is not set. Refusing to run.")
        return 2

    with io.open(HTML_PATH, encoding="utf-8") as fh:
        html = fh.read()

    # --- artefact sanity gates -------------------------------------------------
    gates = [
        ("html file exists and is non-trivial", len(html) >= MIN_HTML_BYTES,
         "{0:,} bytes".format(len(html))),
        ("contains the Seller Hub anchor 837.93", "837.93" in html, ""),
        ("contains all 30 data rows", html.count("<tr data-account") == 30,
         "found {0}".format(html.count("<tr data-account"))),
        ("self-contained (no external http refs)",
         'src="http' not in html and 'href="http' not in html, ""),
        ("carries the Active Listing caveat", "understated by roughly" in html, ""),
        ("shows EUR rows in euros, not pounds", "€1,083.95" in html, ""),
        ("no blended cross-currency total", "£2,983.35" not in html, ""),
    ]
    print("\nArtefact gates")
    for name, ok, extra in gates:
        print("  [{0}] {1}{2}".format("PASS" if ok else "FAIL", name,
                                      "  ({0})".format(extra) if extra else ""))
    if not all(ok for _n, ok, _e in gates):
        print("\nA gate failed. Nothing published.")
        return 1

    conn = psycopg2.connect(**DB)
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT MAX(id) FROM tech_team_outputs.ph_task")
                max_id = cur.fetchone()[0]

                plan = []
                for user in RECIPIENTS:
                    tid = task_id_for(user)
                    cur.execute(
                        "SELECT id, version_level FROM tech_team_outputs.ph_task "
                        "WHERE task_id = %s", (tid,))
                    found = cur.fetchall()
                    if len(found) > 1:
                        print("\nAMBIGUOUS: task_id {0!r} matches {1} rows. "
                              "Refusing to guess.".format(tid, len(found)))
                        return 1
                    if found:
                        plan.append(("UPDATE", found[0][0], user, tid, found[0][1] + 1))
                    else:
                        plan.append(("INSERT", None, user, tid, 1))

                print("\nPlanned rows  (audience: {0})".format(AUDIENCE))
                print("  {0:<7} {1:<7} {2:<11} {3:<34} {4}".format(
                    "ACTION", "ID", "USER", "TASK_ID", "VER"))
                for action, rid, user, tid, ver in plan:
                    shown_id = rid if rid else "new"
                    print("  {0:<7} {1:<7} {2:<11} {3:<34} v{4}".format(
                        action, shown_id, user, tid, ver))

                n_new = sum(1 for p in plan if p[0] == "INSERT")
                if n_new:
                    print("\n  {0} new rows would take ids {1}-{2} (current max {3})".format(
                        n_new, max_id + 1, max_id + n_new, max_id))

                if not args.commit:
                    print("\nDRY RUN - nothing written. Re-run with --commit to publish.\n")
                    return 0

                for action, rid, user, tid, ver in plan:
                    if action == "UPDATE":
                        cur.execute(
                            """UPDATE tech_team_outputs.ph_task
                               SET html_content=%s, task_name=%s, project_name=%s,
                                   assigned_user_team=%s, version_level=%s,
                                   version_status=%s, description=%s, updated_at=now()
                               WHERE id=%s""",
                            (html, TASK_NAME, PROJECT_NAME, AUDIENCE, ver,
                             VERSION_STATUS, DESCRIPTION, rid))
                    else:
                        cur.execute(
                            """INSERT INTO tech_team_outputs.ph_task
                               (project_name, project_code, task_name, task_id, team,
                                developer, assigned_user, assigned_user_team, html_content,
                                description, phase_level, version_level, version_status)
                               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                               RETURNING id""",
                            (PROJECT_NAME, PROJECT_CODE, TASK_NAME, tid, TEAM, DEVELOPER,
                             user, AUDIENCE, html, DESCRIPTION, PHASE_LEVEL, ver,
                             VERSION_STATUS))
                        rid = cur.fetchone()[0]
                    print("  {0} id={1} {2}".format(action.lower() + "d", rid, tid))
        print("\nPublished {0} rows.\n".format(len(RECIPIENTS)))
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
