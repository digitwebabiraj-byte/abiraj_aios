# -*- coding: utf-8 -*-
"""
REQ-16-D01 — publish the eBay Slow Moving & No Moving Products dashboard to
`tech_team_outputs.ph_task` for the **ebay_priors** audience.

Run a dry run first (default). Nothing is written without --publish:

    python publish_esnm_ph_task.py                # DRY RUN - shows the exact plan
    python publish_esnm_ph_task.py --publish      # actually writes

----------------------------------------------------------------------------------------------
TRAPS THIS SCRIPT EXISTS TO AVOID  (all verified live against the real table, 2026-07-22)
----------------------------------------------------------------------------------------------
1. **`assigned_user_team` is missing from the sample DDL but is REAL and required.**
   Without it the row is invisible to the ebay_priors audience. The sample script does not
   mention it at all.

2. **There is NO unique constraint on `task_id`.** The sample DDL claims
   `CONSTRAINT ph_task_task_id_unique UNIQUE (task_id)` — it does not exist on the live table.
   Consequences:
     * `INSERT ... ON CONFLICT (task_id)` raises "no unique or exclusion constraint matching"
     * a blind INSERT silently creates DUPLICATE rows and the PH sees the report twice
   So this script SELECTs by task_id first and UPDATEs in place, and refuses to proceed if it
   ever finds more than one row for a task_id.

3. **One row PER USER.** ebay_priors is 4 people (Jarsini, kobiga, powsteena, Thinesh) and the
   established eBay convention (see epd rows 395-398) is one ph_task row each, not one shared
   row. Publishing a single row would deliver the report to only one of them.

4. **Never assert `version_status` after writing.** Staff change it themselves (row 401 sits at
   'completed'). A post-write assertion that it equals 'released' would fail on any row a user
   has actioned, and re-forcing it would roll back their action. We set it on write and then
   leave it alone. Precedent: PRJ-2026-010 / EPPA.

5. **version_level increments, never resets** — matching epd (v2) and eppa (v3).
----------------------------------------------------------------------------------------------

Credentials come from the environment (global credential store) — never hardcoded.
"""
import os, sys, io, hashlib
import psycopg2

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, ".."))
HTML = os.path.join(PROJ, "evidence", "final_outputs",
                    "REQ-16_ebay-slow-no-moving-products",
                    "REQ-16-D01_esnm_dashboard.html")

# ---------------------------------------------------------------- publish definition
PROJECT_NAME = "eBay Slow Moving & No Moving Products"
PROJECT_CODE = "esnm"
TASK_NAME    = "REQ-16-D01 eBay Slow Moving & No Moving Products — UK + Germany"
TEAM         = "Development"
DEVELOPER    = "Abiraj"
AUDIENCE     = "ebay_priors"
RECIPIENTS   = ["Thinesh", "Jarsini", "kobiga", "powsteena"]
PERIOD       = "2026-07"
# Deliberately NULL. The portal renders a DESCRIPTION panel above the report from this
# column, which stole ~90px of vertical space from the dashboard inside an already short
# panel (owner instruction 2026-07-22). Nothing is lost: every caveat that used to live
# here (Watchers unavailable, 11 lost traffic days, listed-qty != inventory) is stated on
# the report itself, in the footer strip and on the column tooltips.
DESCRIPTION  = None

def task_id_for(user):
    return "%s_%s_ebay_slow_no_moving_products_%s" % (PROJECT_CODE, user, PERIOD)


def conn():
    return psycopg2.connect(
        host=os.getenv("PGHOST", "149.28.134.54"), port=os.getenv("PGPORT", "5435"),
        dbname=os.getenv("PGDATABASE", "order_management_copy"),
        user=os.getenv("PGUSER", "temp_user"), password=os.environ["PGPASSWORD"],
        connect_timeout=30)


def main():
    publish = "--publish" in sys.argv

    if not os.path.isfile(HTML):
        sys.exit("HTML not found: %s" % HTML)
    html = io.open(HTML, encoding="utf-8").read()
    sha = hashlib.sha256(html.encode("utf-8")).hexdigest()

    # --- refuse to publish an artefact that is obviously not the report -------------
    guards = [
        ("file size >= 1 MB",              len(html) >= 1_000_000),
        ("contains the payload block",     '<script id="payload"' in html),
        ("contains the report title",      "Slow Moving" in html),
        ("no unreplaced template tokens",  "__DATA__" not in html),
    ]
    print("Artefact: %s" % os.path.basename(HTML))
    print("  bytes  : %s" % format(len(html.encode('utf-8')), ','))
    print("  sha256 : %s" % sha[:32])
    for label, okv in guards:
        print("  %-30s %s" % (label, "OK" if okv else "FAIL"))
    if not all(o for _, o in guards):
        sys.exit("Refusing to publish — artefact failed a sanity guard.")

    c = conn()
    try:
        with c:
            with c.cursor() as cur:
                # who is really in this audience today
                cur.execute("""SELECT DISTINCT assigned_user FROM tech_team_outputs.ph_task
                               WHERE assigned_user_team = %s""", (AUDIENCE,))
                known = {r[0] for r in cur.fetchall()}
                unknown = [u for u in RECIPIENTS if u not in known]
                print("\nAudience '%s' — existing members: %s" % (AUDIENCE, ", ".join(sorted(known))))
                if unknown:
                    print("  !! not previously seen in this audience: %s" % ", ".join(unknown))

                plan = []
                for user in RECIPIENTS:
                    tid = task_id_for(user)
                    cur.execute("""SELECT id, version_level, version_status, assigned_user_team,
                                          length(coalesce(html_content,''))
                                   FROM tech_team_outputs.ph_task WHERE task_id = %s
                                   ORDER BY id""", (tid,))
                    rows = cur.fetchall()
                    if len(rows) > 1:
                        sys.exit("ABORT: %d rows already share task_id %s — resolve by hand "
                                 "(there is no unique constraint to protect us)." % (len(rows), tid))
                    plan.append((user, tid, rows[0] if rows else None))

                print("\n%-11s %-52s %s" % ("USER", "TASK_ID", "ACTION"))
                for user, tid, row in plan:
                    if row:
                        print("%-11s %-52s UPDATE id=%s  v%s -> v%s (status %s left untouched)"
                              % (user, tid, row[0], row[1], row[1] + 1, row[2]))
                    else:
                        print("%-11s %-52s INSERT new row (v1, released)" % (user, tid))

                if not publish:
                    print("\nDRY RUN — nothing written. Re-run with --publish to apply.")
                    return

                for user, tid, row in plan:
                    if row:
                        cur.execute("""
                            UPDATE tech_team_outputs.ph_task
                               SET html_content       = %s,
                                   project_name       = %s,
                                   project_code       = %s,
                                   task_name          = %s,
                                   team               = %s,
                                   developer          = %s,
                                   assigned_user      = %s,
                                   assigned_user_team = %s,
                                   description        = %s,
                                   phase_level        = 1,
                                   version_level      = version_level + 1,
                                   version_status     = 'released',
                                   updated_at         = now()
                             WHERE id = %s
                        """, (html, PROJECT_NAME, PROJECT_CODE, TASK_NAME, TEAM, DEVELOPER,
                              user, AUDIENCE, DESCRIPTION, row[0]))
                        print("  updated id=%s (%s) rowcount=%d" % (row[0], user, cur.rowcount))
                    else:
                        cur.execute("""
                            INSERT INTO tech_team_outputs.ph_task
                                (project_name, project_code, task_name, task_id, team, developer,
                                 assigned_user, assigned_user_team, html_content, description,
                                 phase_level, version_level, version_status, created_at, updated_at)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,1,1,'released',now(),now())
                            RETURNING id
                        """, (PROJECT_NAME, PROJECT_CODE, TASK_NAME, tid, TEAM, DEVELOPER,
                              user, AUDIENCE, html, DESCRIPTION))
                        print("  inserted id=%s (%s)" % (cur.fetchone()[0], user))

        # --- verify OUTSIDE the write transaction ---------------------------------
        with c.cursor() as cur:
            print("\n=== VERIFY ===")
            cur.execute("""SELECT id, task_id, assigned_user, assigned_user_team, version_level,
                                  version_status, length(html_content), updated_at
                             FROM tech_team_outputs.ph_task
                            WHERE task_id = ANY(%s) ORDER BY id""",
                        ([task_id_for(u) for u in RECIPIENTS],))
            got = cur.fetchall()
            for r in got:
                print("  id=%-4s %-52s %-10s %-12s v%s %-9s %s bytes  %s"
                      % (r[0], r[1], r[2], r[3], r[4], r[5], format(r[6], ','), r[7]))
            assert len(got) == len(RECIPIENTS), \
                "expected %d rows, found %d" % (len(RECIPIENTS), len(got))
            assert all(r[3] == AUDIENCE for r in got), "an audience value is wrong"
            assert all(r[6] == len(html) for r in got), "stored html length mismatch"
            # NB: deliberately NO assertion on version_status - see trap 4 in the docstring.
            print("  all %d rows present, audience correct, html length matches" % len(got))
    finally:
        c.close()


if __name__ == "__main__":
    main()
