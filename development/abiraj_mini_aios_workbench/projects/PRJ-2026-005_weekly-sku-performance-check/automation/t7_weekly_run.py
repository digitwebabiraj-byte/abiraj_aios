# -*- coding: utf-8 -*-
"""
T7 - Weekly SKU Performance Check (Thuwaraga) - AUTONOMOUS weekly run (REQ-07-D02).
Headless (no MCP, no human): pull -> validate -> render -> guarded publish to ph_task -> log.

Automates the CLOSED-and-SIGNED-OFF REQ-07-D01 report (Thuwaraga + Satheewaran, 2026-07-09).
Nothing about the report's method changes here; the only thing this adds is the dynamic window
and the schedule, which the canonical SQL and TASK_REGISTER both named as the open item.

WINDOW (business rule, from generate_dataset.sql): runs every Thursday; the window is the rolling
7 days ending the day BEFORE the run date (Thu run -> last Thu .. last Wed). Computed from the
DATABASE's CURRENT_DATE, not the local clock, so the window matches the data being counted.
Today is never included - marketplace orders keep settling for ~1-2 days.

Connection (password NEVER hardcoded - normally the global credential store,
see 05_documentation/capability/shared_db_credentials/):
  warehouse (reads + ph_task write): PGHOST PGPORT PGDATABASE PGUSER PGPASSWORD
This report needs ONE database. Source tables are READ-ONLY; the only write is the guarded
single-row publish into tech_team_outputs.ph_task.

FAILS CLOSED: every gate runs BEFORE any write. Any failure -> non-zero exit, nothing published.
Exit codes: 0 ok · 1 config/credential · 2 integrity gate failed (nothing published)
            3 DB error · 4 publish verify failed (rolled back)

Flags:
  --dry-run / --no-publish   validate + build only, write nothing
  --window YYYY-MM-DD        override the window start (that date .. +6 days), for regression tests
Usage:  python t7_weekly_run.py [--dry-run] [--window 2026-07-02]

Requires: build_html.py from evidence/final_outputs/T7_weekly-sku-performance-check (the dashboard
UI is that file and only that file - this runner never re-implements the rendering).
"""
import os, sys, time, json, hashlib, datetime

import psycopg2

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
RENDER_DIR = os.path.join(PROJECT, "evidence", "final_outputs", "T7_weekly-sku-performance-check")

PUBLISH = not ("--no-publish" in sys.argv or "--dry-run" in sys.argv)
WINDOW_OVERRIDE = None
if "--window" in sys.argv:
    try:
        WINDOW_OVERRIDE = sys.argv[sys.argv.index("--window") + 1]
        datetime.date.fromisoformat(WINDOW_OVERRIDE)
    except (IndexError, ValueError):
        print("[T7] --window needs a date, e.g. --window 2026-07-02", flush=True)
        sys.exit(1)

# ---- locked identity (matches the live ph_task row 135 - do not re-mint) ----
PROJECT_CODE = "WSPC"
TASK_ID      = "WSPC_thuwaraga_SKU_Performance_Dashboard-V1"
PROJECT_NAME = "Weekly SKU Performance Check — Thuwaraga UK (Amazon · eBay · B&Q)"
TASK_NAME    = "T7 · Weekly SKU Performance Check — Thuwaraga UK (Amazon · eBay · B&Q)"
TEAM, DEVELOPER = "Development", "Abiraj"
ASSIGNED_USER, ASSIGNED_USER_TEAM = "thuwaraga", "ph_priors"

# ---- locked data rules (from the signed-off canonical SQL - do not change here) ----
PH_USER   = "thuwaraga"
PLATFORMS = ("AMAZON", "EBAY", "B&Q")
MIN_ROWS  = int(os.getenv("T7_MIN_ROWS", "500"))     # catastrophic-failure floor (expect ~2,140)

# The signed-off D01 reference window and its validated totals. Running --window 2026-07-02
# must reproduce these exactly; that is this runner's regression test.
ANCHOR_WINDOW  = "2026-07-02"
ANCHOR_LISTINGS, ANCHOR_ORDERS, ANCHOR_FAMILIES = 2140, 170, 218

WH = dict(host=os.getenv("PGHOST", "149.28.134.54"), port=os.getenv("PGPORT", "5435"),
          dbname=os.getenv("PGDATABASE", "order_management_copy"),
          user=os.getenv("PGUSER", "temp_user"), password=os.getenv("PGPASSWORD"))


def log(m): print("[T7] " + m, flush=True)


def _status(state, msg):
    try:
        with open(os.path.join(HERE, "t7_status.txt"), "a", encoding="utf-8") as f:
            f.write("[%s]  %s  |  %s\n"
                    % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), state, msg))
    except Exception:
        pass


def die(code, m):
    log("ABORT: " + m + "  -> nothing published")
    _status("FAILED", m)
    sys.exit(code)


def connect():
    """Connect with retry - the shared temp_user pool intermittently returns 'too many clients'."""
    last = None
    for attempt in range(1, 6):
        try:
            c = psycopg2.connect(connect_timeout=20, **WH)
            c.set_client_encoding("UTF8")
            return c
        except Exception as e:
            last = e
            log("  warehouse connect attempt %d failed: %s"
                % (attempt, str(e).strip().splitlines()[0]))
            time.sleep(8)
    die(3, "cannot connect to the warehouse after 5 attempts: %s" % last)


# ---- 1. THE CANONICAL QUERY -------------------------------------------------
# Copied verbatim from sql/T7_weekly-sku-performance-check/generate_dataset.sql, with the one
# change that file itself prescribes: the hard-coded win CTE becomes bound parameters.
SQL = """
WITH win AS (SELECT %(ws)s::date AS ws, %(we)s::date AS we),
universe AS (
    SELECT DISTINCT
        ot."sku"                                                AS sku,
        COALESCE(NULLIF(ot."asin",''), NULLIF(ot."item_id",'')) AS ref,
        ot."source_name"                                        AS platform,
        ot."ss_name"                                            AS account
    FROM public.order_transaction ot
    WHERE LOWER(ot."user_name") = LOWER(%(ph)s)
      AND ot."market_place" = 'UK'
      AND ot."source_name" IN ('AMAZON','EBAY','B&Q')
),
orders AS (
    SELECT
        ot."sku"                                                AS sku,
        COALESCE(NULLIF(ot."asin",''), NULLIF(ot."item_id",'')) AS ref,
        ot."source_name"                                        AS platform,
        ot."ss_name"                                            AS account,
        COUNT(DISTINCT ot."order_item_info")                    AS orders
    FROM public.order_transaction ot, win
    WHERE LOWER(ot."user_name") = LOWER(%(ph)s)
      AND ot."market_place" = 'UK'
      AND ot."source_name" IN ('AMAZON','EBAY','B&Q')
      AND ot."order_status" = 'Completed'
      AND ot."order_date"::date BETWEEN win.ws AND win.we
    GROUP BY 1,2,3,4
),
ld_agg AS (
    SELECT ld."sku"                                             AS sku,
           COALESCE(NULLIF(MAX(NULLIF(ld."mapped_sku",'')),''), ld."sku") AS base_sku,
           MAX(NULLIF(ld."title",''))                           AS title
    FROM public.listing_data ld
    WHERE ld."wrong_sku" = 0
    GROUP BY ld."sku"
),
cat AS (
    SELECT ot."sku" AS sku,
           MODE() WITHIN GROUP (ORDER BY ot."category_name") AS category
    FROM public.order_transaction ot
    WHERE LOWER(ot."user_name") = LOWER(%(ph)s)
      AND ot."category_name" IS NOT NULL AND ot."category_name" <> ''
    GROUP BY ot."sku"
)
SELECT
    u."sku"                                                     AS sku,
    u."ref"                                                     AS ref_id,
    u."platform",
    u."account",
    COALESCE(la.base_sku, u."sku")                              AS base_sku,
    CASE WHEN la.base_sku IS NOT NULL AND la.base_sku <> u."sku"
         THEN 1 ELSE 0 END                                      AS mapped_flag,
    COALESCE(NULLIF(la.title,''), c.category, '')                AS product_name,
    COALESCE(o.orders, 0)                                       AS orders
FROM universe u
CROSS JOIN win
LEFT JOIN orders o
       ON o.sku      IS NOT DISTINCT FROM u."sku"
      AND o.ref      IS NOT DISTINCT FROM u."ref"
      AND o.platform =  u."platform"
      AND o.account  IS NOT DISTINCT FROM u."account"
LEFT JOIN ld_agg la ON la.sku = u."sku"
LEFT JOIN cat    c  ON c.sku  = u."sku"
ORDER BY base_sku, u."platform", u."ref";
"""

# Independent control total: the same window counted straight off the source table, without the
# universe/join machinery. If the assembled report disagrees with this, the pull drifted.
SQL_CONTROL = """
SELECT COUNT(DISTINCT ot."order_item_info")
FROM public.order_transaction ot
WHERE LOWER(ot."user_name") = LOWER(%(ph)s)
  AND ot."market_place" = 'UK'
  AND ot."source_name" IN ('AMAZON','EBAY','B&Q')
  AND ot."order_status" = 'Completed'
  AND ot."order_date"::date BETWEEN %(ws)s::date AND %(we)s::date;
"""


def main():
    if not WH["password"]:
        die(1, "warehouse PGPASSWORD not set - see "
               "05_documentation/capability/shared_db_credentials/")

    conn = connect()
    try:
        with conn.cursor() as cur:
            # ---- 2. WINDOW: from the DB clock, never the local one ----------
            cur.execute("SELECT CURRENT_DATE")
            db_today = cur.fetchone()[0]
            if WINDOW_OVERRIDE:
                ws = datetime.date.fromisoformat(WINDOW_OVERRIDE)
                we = ws + datetime.timedelta(days=6)
                log("window OVERRIDE: %s .. %s (regression mode)" % (ws, we))
            else:
                we = db_today - datetime.timedelta(days=1)      # yesterday, inclusive
                ws = we - datetime.timedelta(days=6)            # rolling 7 days
            if we >= db_today:
                die(2, "window end %s is not before the DB's today %s" % (we, db_today))
            if (we - ws).days != 6:
                die(2, "window is %d days, expected 7" % ((we - ws).days + 1))
            log("run date %s (DB) | window %s .. %s | publish=%s" % (db_today, ws, we, PUBLISH))

            args = {"ph": PH_USER, "ws": ws.isoformat(), "we": we.isoformat()}
            cur.execute(SQL, args)
            raw = cur.fetchall()
            cur.execute(SQL_CONTROL, args)
            db_orders = cur.fetchone()[0]
    except SystemExit:
        raise
    except Exception as e:
        die(3, "query failed: %s" % str(e).strip().splitlines()[0])

    # ---- 3. ASSEMBLE the renderer's data contract -------------------------
    rows, names = [], {}
    for sku, ref, platform, account, base_sku, mapped_flag, product_name, orders in raw:
        rows.append({"s": sku, "r": ref, "p": platform, "a": account,
                     "b": base_sku, "m": int(mapped_flag), "o": int(orders)})
        if product_name:
            names.setdefault(sku, product_name)
            names.setdefault(base_sku, product_name)
    n_amzn_gr = len({r["s"] for r in rows if str(r["s"]).startswith("amzn.gr.")})
    report_orders = sum(r["o"] for r in rows)
    performing = sum(1 for r in rows if r["o"] > 0)
    dirty_mapped = sum(1 for r in rows if r["m"])
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    data = {
        "meta": {
            "report": "Table 7 - Weekly SKU Performance Check",
            "portfolio_holder": "Thuwaraga",
            "project_code": "PH-2026-07-THUW07",
            "run_date": db_today.isoformat(),
            "week_start": ws.isoformat(),
            "week_end": we.isoformat(),
            "database": WH["dbname"],
            "source_user_name": PH_USER,
            "platforms": list(PLATFORMS),
            "snapshot_at": stamp,
            "snapshot_note": ("Live DB - marketplace orders for a just-ended window keep settling "
                              "for ~1-2 days; counts are as-of the snapshot above."),
            "excluded_amzn_gr_group_ids": n_amzn_gr,
        },
        "names": names,
        "rows": rows,
    }
    log("pulled %d listing rows | %d performing | %d orders | %d dirty mapped_sku | %d amzn.gr.*"
        % (len(rows), performing, report_orders, dirty_mapped, n_amzn_gr))

    # ---- 4. VALIDATION GATES (fail closed, BEFORE any write) --------------
    if not rows:                    die(2, "0 listing rows - refusing to publish an empty report")
    if len(rows) < MIN_ROWS:        die(2, "only %d rows (< floor %d) - looks like a broken pull"
                                           % (len(rows), MIN_ROWS))
    bad_platform = sorted({r["p"] for r in rows} - set(PLATFORMS))
    if bad_platform:                die(2, "unexpected platform(s) in the pull: %s" % bad_platform)
    if any(r["o"] < 0 for r in rows):
        die(2, "a listing has a negative order count")
    if any(not r["s"] for r in rows):
        die(2, "a listing row has no SKU - grain unsafe")
    seen = set()
    dupes = [k for k in ((r["s"], r["r"], r["p"], r["a"]) for r in rows)
             if k in seen or seen.add(k)]
    if dupes:                       die(2, "grain broken - %d duplicated listing key(s): %s"
                                           % (len(dupes), dupes[:3]))
    if report_orders != db_orders:
        die(2, "control totals disagree: report %d orders vs direct DB count %d"
               % (report_orders, db_orders))
    log("control total reconciles: %d Completed orders (report) == %d (direct DB count)"
        % (report_orders, db_orders))

    # ---- 5. RENDER via the signed-off renderer, never a re-implementation --
    sys.path.insert(0, RENDER_DIR)
    try:
        import build_html as BH
        groups = BH.build_groups(data)
        html = BH.render(data, groups)
    except Exception as e:
        die(2, "render failed: %s" % str(e).strip().splitlines()[-1])
    if len(groups) == 0:            die(2, "0 SKU families after grouping - render would be empty")
    if len(html) < 100_000:         die(2, "dashboard only %d bytes - render looks broken" % len(html))
    html_md5 = hashlib.md5(html.encode("utf-8")).hexdigest()
    log("rendered %d SKU families | %d bytes | md5 %s" % (len(groups), len(html), html_md5[:8]))

    # ---- 6. REGRESSION TEST against the signed-off D01 run -----------------
    # Run with --window 2026-07-02 to check this runner still reproduces D01.
    #
    # It does NOT assert D01's headline totals, because those legitimately move: the `universe`
    # CTE is not window-bounded (new listings keep appearing) and marketplace orders keep settling
    # after the run. Measured 2026-07-21 against the same window: 2,140 -> 2,166 listings
    # (+26 new, ZERO lost) and 170 -> 183 orders (+13, every one an increment on a row D01 already
    # had, e.g. 3->4). Asserting equality would fail forever on correct data.
    #
    # The stable invariant is CONTAINMENT: every listing D01 reported must still be produced.
    # A lost row means the query drifted; extra rows are the world moving on.
    if ws.isoformat() == ANCHOR_WINDOW:
        d01 = os.path.join(RENDER_DIR, "data.json")
        if not os.path.exists(d01):
            die(2, "regression mode needs D01's data.json at %s" % d01)
        with open(d01, encoding="utf-8") as f:
            old = json.load(f)
        old_keys = {(r["s"], r["r"], r["p"], r["a"]) for r in old["rows"]}
        new_keys = {(r["s"], r["r"], r["p"], r["a"]) for r in rows}
        lost = old_keys - new_keys
        if lost:
            die(2, "D01 regression FAILED: %d listing(s) D01 reported are no longer produced: %s"
                   % (len(lost), sorted(lost)[:3]))
        log("D01 regression PASSED: all %d signed-off listings still produced "
            "(+%d new, 0 lost) | orders %d -> %d, families %d -> %d"
            % (len(old_keys), len(new_keys) - len(old_keys), ANCHOR_ORDERS, report_orders,
               ANCHOR_FAMILIES, len(groups)))
    log("validation: all gates PASSED")

    out_html = os.path.join(HERE, "t7_auto_dashboard.html")
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(html)
    log("dashboard written: %s (%d bytes)" % (out_html, len(html)))

    summary = ("%s..%s | %d listings | %d performing | %d orders | %d families"
               % (ws, we, len(rows), performing, report_orders, len(groups)))
    if not PUBLISH:
        log("--dry-run: validated and built, wrote nothing to ph_task.")
        _status("OK(dry-run)", summary + " | built only")
        log("done.")
        return

    # ---- 7. GUARDED PUBLISH: one transaction, md5-verified before commit ---
    desc = ("T7 Weekly SKU Performance Check (REQ-07-D01) - auto weekly refresh %s. "
            "Rolling 7 days %s..%s across Amazon / eBay / B&Q UK for Thuwaraga: %d listings in "
            "%d product families, %d performing, %d Completed orders."
            % (db_today, ws, we, len(rows), len(groups), performing, report_orders))
    try:
        with conn:                                   # one transaction; auto-rollback on exception
            with conn.cursor() as cur:
                cur.execute("""UPDATE tech_team_outputs.ph_task
                                  SET html_content=%s, description=%s,
                                      version_level=version_level+1, updated_at=now()
                                WHERE project_code=%s AND task_id=%s RETURNING id""",
                            (html, desc, PROJECT_CODE, TASK_ID))
                got = cur.fetchall()
                if len(got) == 1:
                    rid, how = got[0][0], "UPDATE"
                elif len(got) == 0:                  # row absent (first run / cleared store)
                    cur.execute("""INSERT INTO tech_team_outputs.ph_task
                        (project_name,project_code,task_name,task_id,team,developer,assigned_user,
                         assigned_user_team,html_content,description,phase_level,version_level,
                         version_status,created_at,updated_at)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,1,1,'released',now(),now())
                        RETURNING id""",
                        (PROJECT_NAME, PROJECT_CODE, TASK_NAME, TASK_ID, TEAM, DEVELOPER,
                         ASSIGNED_USER, ASSIGNED_USER_TEAM, html, desc))
                    rid, how = cur.fetchone()[0], "INSERT (row was absent)"
                else:
                    raise RuntimeError("task_id %s matched %d rows - aborting" % (TASK_ID, len(got)))

                cur.execute("SELECT md5(html_content), assigned_user_team, version_status "
                            "FROM tech_team_outputs.ph_task WHERE id=%s", (rid,))
                stored_md5, team_tag, ver_status = cur.fetchone()
                if stored_md5 != html_md5:
                    raise RuntimeError("md5 verify failed pre-commit (id=%s) - rolling back" % rid)
                if team_tag != ASSIGNED_USER_TEAM or ver_status != "released":
                    raise RuntimeError("routing broken (id=%s team=%s status=%s) - rolling back"
                                       % (rid, team_tag, ver_status))
                log("  %s id=%s md5=%s team=%s" % (how, rid, html_md5[:8], team_tag))
    except Exception as e:
        die(4, "publish failed, transaction rolled back: %s" % str(e).strip().splitlines()[-1])
    finally:
        conn.close()

    log("PUBLISHED + COMMITTED to ph_task, md5-verified.")
    _status("OK", summary + " | PUBLISHED")
    log("done.")


if __name__ == "__main__":
    main()
