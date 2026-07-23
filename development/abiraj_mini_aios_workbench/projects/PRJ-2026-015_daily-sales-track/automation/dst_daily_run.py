# -*- coding: utf-8 -*-
"""
REQ-17-D02 — Daily Sales Track, autonomous daily run.

Pulls live, rebuilds all three REQ-17-D01 artefacts, and refreshes the four ph_task rows.
Runs headless with no MCP: direct psycopg2 against the same two databases.

    python dst_daily_run.py              # full run, publishes
    python dst_daily_run.py --dry-run    # rebuild + all gates, publishes NOTHING
    python dst_daily_run.py --date 2026-07-22   # re-run a specific reporting day

ANCHOR (decision B): a run on date R reports R-1 as "Today" and R-2 as "Yesterday";
Same Day LY is the same CALENDAR date one year before R-1 (decision C). The dates are
computed from the RUN DATE and pinned into the SQL as literals - never CURRENT_DATE,
because the warehouse runs on Asia/Colombo and would roll over 4.5h before London.

SALES (decision M): every order PLACED that day, excluding status 'Cancelled' only.
Orders only reach 'Completed' about two days after purchase, so a Completed-only filter
would understate the reported day by roughly 69% and read as a crash every morning.

MONEY IS NEVER SUMMED ACROSS CURRENCIES. orders.total is in the marketplace's own
currency and neither database holds an exchange rate.

FAIL-CLOSED: every gate must pass before anything is published. On failure the previous
day's report stays live, a line is written to dst_status.txt, and a desktop alert fires.
"""

import argparse
import datetime as dt
import hashlib
import io
import json
import os
import sys
import time
import traceback

import psycopg2

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, ".."))
SQL_DIR = os.path.join(PROJ, "sql", "REQ-17_daily-sales-track")
OUT_DIR = os.path.join(PROJ, "evidence", "final_outputs", "REQ-17_daily-sales-track")
STATUS = os.path.join(HERE, "dst_status.txt")
LAST_GOOD = os.path.join(HERE, "dst_last_good.json")

sys.path.insert(0, SQL_DIR)

LEDSONE = {
    "host": os.getenv("LED_PGHOST", "207.148.78.148"),
    "port": os.getenv("LED_PGPORT", "5432"),
    "dbname": os.getenv("LED_PGDATABASE", "ledsone"),
    "user": os.getenv("LED_PGUSER", "dbhub_readonly"),
    "password": os.getenv("LED_PGPASSWORD"),
}
WAREHOUSE = {
    "host": os.getenv("PGHOST", "149.28.134.54"),
    "port": os.getenv("PGPORT", "5435"),
    "dbname": os.getenv("PGDATABASE", "order_management_copy"),
    "user": os.getenv("PGUSER", "temp_user"),
    "password": os.getenv("PGPASSWORD"),
}

RECIPIENTS = ["Thinesh", "Jarsini", "kobiga", "powsteena"]
AUDIENCE = "ebay_priors"

# --- fail-closed thresholds -------------------------------------------------
MIN_ROWS = 20          # the universe is ~30 account x marketplace rows
MIN_ORDERS = 20        # a normal day is 110-175 orders across the channel
MAX_ROW_COLLAPSE = 0.40    # refuse if rows fall >40% vs the last good run
MAX_ORDER_COLLAPSE = 0.70  # orders swing far more than rows; only a near-total loss is a fault
MIN_HTML_BYTES = 20000


def log(msg):
    line = "{0}  {1}".format(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg)
    print(line)
    with io.open(STATUS, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def status(state, msg):
    """One machine-readable verdict per run, so check_status.bat and a human both get an
    answer without reading the whole log. Fleet pattern, copied from EPC."""
    log("STATUS {0} | {1}".format(state, msg))


def die(msg):
    """Record the verdict, then abort. Nothing downstream runs."""
    status("FAILED", msg)
    raise RuntimeError(msg)


def connect(cfg, label, attempts=7):
    """Retry rather than lose the day.

    The warehouse sits behind ONE restricted `temp_user` login shared by the whole fleet,
    on a server whose max_connections is 100. Observed 2026-07-23: 108 live connections,
    temp_user holding zero - it simply could not get a slot, and a 60-second retry budget
    was not enough. Backoff is now 15/30/60/90/120/180s, about 8 minutes total. For a job
    that runs once a day and takes ten seconds, waiting is far cheaper than losing the day.
    """
    delays = [15, 30, 60, 90, 120, 180]
    last = None
    for i in range(attempts):
        try:
            c = psycopg2.connect(connect_timeout=20, **cfg)
            if i:
                log("  {0}: connected on attempt {1}".format(label, i + 1))
            return c
        except Exception as exc:          # noqa: BLE001 - retrying any connection error
            last = exc
            if i < attempts - 1:
                wait = delays[min(i, len(delays) - 1)]
                log("  {0}: attempt {1} failed, retrying in {2}s".format(label, i + 1, wait))
                time.sleep(wait)
    raise RuntimeError("{0}: could not connect after {1} attempts (~8 min): {2}".format(
        label, attempts, last))


def rows_from_live(cur, d_r1, d_r2, d_ly):
    """One row per account x marketplace, from the raw ledsone DB."""
    a, b, c = d_r1.isoformat(), d_r2.isoformat(), d_ly.isoformat()

    cur.execute("""
        WITH ph AS (SELECT DISTINCT ref_id FROM staff.ph_category_products WHERE source_id = 2)
        SELECT ss.name, el.site,
               COUNT(DISTINCT el.item_id),
               COUNT(DISTINCT el.item_id) FILTER (WHERE ph.ref_id IS NOT NULL),
               COUNT(DISTINCT el.item_id) FILTER (WHERE ph.ref_id IS NULL)
        FROM listings.ebay_listings el
        JOIN order_management.sub_source ss ON ss.id = el.sub_source AND ss.source_id = 2
        LEFT JOIN ph ON ph.ref_id = el.item_id
        WHERE el.is_ended = 0 AND el.all_list = 1   -- AIOS KB rule, never is_child/is_parent
          AND el.site IS NOT NULL
        GROUP BY 1, 2""")
    listings = {(r[0], r[1]): (r[2], r[3], r[4]) for r in cur.fetchall()}

    cur.execute("""
        SELECT ss.name, mp.name,
          COALESCE(SUM(o.total) FILTER (WHERE o.order_date::date = %s), 0),
          COALESCE(SUM(o.total) FILTER (WHERE o.order_date::date = %s), 0),
          COALESCE(SUM(o.total) FILTER (WHERE o.order_date::date = %s), 0),
          COUNT(DISTINCT o.id) FILTER (WHERE o.order_date::date = %s),
          COUNT(DISTINCT o.id) FILTER (WHERE o.order_date::date = %s),
          COUNT(DISTINCT o.id) FILTER (WHERE o.order_date::date = %s)
        FROM order_management.orders o
        JOIN order_management.sub_source ss ON ss.id = o.sub_source_id AND ss.source_id = 2
        LEFT JOIN order_management.market_place mp ON mp.id::text = o.market_place
        WHERE o.status <> 'Cancelled'
          AND o.order_date::date IN (%s, %s, %s)
        GROUP BY 1, 2""", (a, b, c, a, b, c, a, b, c))
    orders = {(r[0], r[1]): r[2:] for r in cur.fetchall()}

    cur.execute("""
        WITH ph AS (SELECT DISTINCT ref_id FROM staff.ph_category_products WHERE source_id = 2)
        SELECT ss.name, mp.name, o.order_date::date,
               SUM(CAST(oii.item_quantity AS INT)),
               COALESCE(SUM(CASE WHEN ph.ref_id IS NOT NULL
                    THEN CAST(oii.item_quantity AS INT) * CAST(oii.item_price AS NUMERIC)
                    ELSE 0 END), 0),
               COALESCE(SUM(CASE WHEN ph.ref_id IS NULL
                    THEN CAST(oii.item_quantity AS INT) * CAST(oii.item_price AS NUMERIC)
                    ELSE 0 END), 0)
        FROM order_management.orders o
        JOIN order_management.sub_source ss ON ss.id = o.sub_source_id AND ss.source_id = 2
        LEFT JOIN order_management.market_place mp ON mp.id::text = o.market_place
        JOIN order_management.order_item_info oii ON oii.order_id = o.id
        LEFT JOIN ph ON ph.ref_id = oii.item_id
        WHERE o.status <> 'Cancelled' AND o.order_date::date IN (%s, %s)
        GROUP BY 1, 2, 3""", (a, b))
    split = {}
    for acct, site, d, units, ph_s, ah_s in cur.fetchall():
        slot = "r1" if d == d_r1 else "r2"
        split.setdefault((acct, site), {})[slot] = (int(units or 0), float(ph_s), float(ah_s))

    from dst_d01_rows import SITE_CURRENCY, DISPLAY, HOLDER_SITE, HOLDER_ACCT, UNASSIGNED

    out = []
    for key in sorted(listings, key=lambda k: (-listings[k][0], k)):
        acct, site = key
        act, ph_l, ah_l = listings[key]
        o = orders.get(key, (0, 0, 0, 0, 0, 0))
        sp = split.get(key, {})
        r1 = sp.get("r1", (0, 0.0, 0.0))
        r2 = sp.get("r2", (0, 0.0, 0.0))
        out.append({
            "key": acct, "site": site,
            "display": DISPLAY.get(acct, acct),
            "holder": HOLDER_SITE.get(key) or HOLDER_ACCT.get(acct) or UNASSIGNED,
            "currency": SITE_CURRENCY[site],
            "s_r1": round(float(o[0]), 2), "s_r2": round(float(o[1]), 2),
            "s_ly": round(float(o[2]), 2),
            "o_r1": int(o[3]), "o_r2": int(o[4]), "o_ly": int(o[5]),
            "units_r1": r1[0],
            "ph_r1": round(r1[1], 2), "ah_r1": round(r1[2], 2),
            "ph_r2": round(r2[1], 2), "ah_r2": round(r2[2], 2),
            "active": act, "ph_l": ph_l, "ah_l": ah_l,
        })
    return out


def gates(rows, d_r1):
    """Every one must pass or nothing is published."""
    import json
    checks = []
    n = len(rows)
    orders = sum(r["o_r1"] for r in rows)
    money = sum(r["s_r1"] for r in rows)

    checks.append(("row count >= {0}".format(MIN_ROWS), n >= MIN_ROWS, "{0} rows".format(n)))
    checks.append(("orders on the reported day >= {0}".format(MIN_ORDERS),
                   orders >= MIN_ORDERS, "{0} orders".format(orders)))
    checks.append(("money is non-zero", money > 0, "{0:,.2f}".format(money)))
    checks.append(("every row carries a currency",
                   all(r.get("currency") for r in rows), ""))
    checks.append(("AH + PH = Active on every row",
                   all(r["ah_l"] + r["ph_l"] == r["active"] for r in rows), ""))
    checks.append(("reported day is in the past",
                   d_r1 < dt.date.today(), d_r1.isoformat()))

    # control totals - the pull must agree with itself
    ccy_sum = {}
    for r in rows:
        ccy_sum[r["currency"]] = round(ccy_sum.get(r["currency"], 0) + r["s_r1"], 2)
    checks.append(("per-currency sums reconcile to the row total",
                   abs(sum(ccy_sum.values()) - round(money, 2)) < 0.01,
                   " · ".join("{0} {1:,.2f}".format(k, v) for k, v in sorted(ccy_sum.items()))))
    checks.append(("listing split reconciles (sum AH + sum PH = sum Active)",
                   sum(r["ah_l"] for r in rows) + sum(r["ph_l"] for r in rows)
                   == sum(r["active"] for r in rows),
                   "{0:,} listings".format(sum(r["active"] for r in rows))))

    prev = None
    if os.path.isfile(LAST_GOOD):
        try:
            prev = json.load(io.open(LAST_GOOD, encoding="utf-8"))
        except Exception:                      # noqa: BLE001
            prev = None
    if prev:
        rd = 1 - (n / float(prev["rows"])) if prev.get("rows") else 0
        od = 1 - (orders / float(prev["orders"])) if prev.get("orders") else 0
        checks.append(("rows have not collapsed vs last good run",
                       rd <= MAX_ROW_COLLAPSE, "{0:+.0%} vs {1}".format(-rd, prev["rows"])))
        checks.append(("orders have not collapsed vs last good run",
                       od <= MAX_ORDER_COLLAPSE, "{0:+.0%} vs {1}".format(-od, prev["orders"])))
    else:
        checks.append(("collapse guard (no baseline yet - skipped)", True, "first run"))
    return checks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="build and gate, publish nothing")
    ap.add_argument("--date", help="reporting day (R-1) as YYYY-MM-DD; default = yesterday")
    args = ap.parse_args()

    import json
    log("=" * 78)
    log("REQ-17-D02 daily run starting{0}".format(" (DRY RUN)" if args.dry_run else ""))

    if args.date:
        d_r1 = dt.date.fromisoformat(args.date)
    else:
        d_r1 = dt.date.today() - dt.timedelta(days=1)
    d_r2 = d_r1 - dt.timedelta(days=1)
    try:
        d_ly = d_r1.replace(year=d_r1.year - 1)
    except ValueError:                 # 29 Feb
        d_ly = d_r1.replace(year=d_r1.year - 1, day=28)
    log("anchor: today={0}  yesterday={1}  same-day-LY={2}".format(d_r1, d_r2, d_ly))

    for cfg, name in ((LEDSONE, "LED_PGPASSWORD"), (WAREHOUSE, "PGPASSWORD")):
        if not cfg["password"]:
            raise RuntimeError("{0} is not set - refusing to run".format(name))

    led = connect(LEDSONE, "ledsone")
    try:
        with led.cursor() as cur:
            rows = rows_from_live(cur, d_r1, d_r2, d_ly)
    finally:
        led.close()
    log("pulled {0} account x marketplace rows".format(len(rows)))

    log("gates:")
    checks = gates(rows, d_r1)
    for name, ok, extra in checks:
        log("  [{0}] {1}{2}".format("PASS" if ok else "FAIL", name,
                                    "  ({0})".format(extra) if extra else ""))
    if not all(ok for _n, ok, _e in checks):
        die("gate failed: " + "; ".join(n for n, ok, _e in checks if not ok))

    # rebuild all three artefacts through the SAME code path D01 used
    import build_dst_d01 as B
    B.ROWS[:] = rows
    B.RUN_DATE, B.D_R1, B.D_R2, B.D_LY = dt.date.today(), d_r1, d_r2, d_ly
    xlsx = B.render_workbook(os.path.join(OUT_DIR, "REQ-17-D01_daily_sales_track.xlsx"))
    js = B.write_governed_json(os.path.join(OUT_DIR, "dst_d01_data.json"))

    import render_dst_dashboard as R
    data = json.load(io.open(js, encoding="utf-8"))
    html_path = R.render(data, os.path.join(OUT_DIR, "REQ-17-D01_dst_dashboard.html"))
    html = io.open(html_path, encoding="utf-8").read()
    if len(html) < MIN_HTML_BYTES:
        raise RuntimeError("dashboard is only {0} bytes - refusing to publish".format(len(html)))
    log("rebuilt: xlsx + json + html ({0:,} bytes)".format(len(html)))

    by_ccy = {}
    for r in rows:
        by_ccy[r["currency"]] = by_ccy.get(r["currency"], 0) + r["s_r1"]
    log("sales {0}".format(" · ".join("{0} {1:,.2f}".format(k, v)
                                      for k, v in sorted(by_ccy.items()))))

    if args.dry_run:
        status("OK(dry-run)", "{0} rows | built only, nothing published".format(len(rows)))
        log("done")
        return 0

    html_md5 = hashlib.md5(html.encode("utf-8")).hexdigest()
    log("payload md5 {0}".format(html_md5[:8]))
    task_name = ("REQ-17-D01 Daily Sales Track — eBay, account × marketplace "
                 "(trading day {0})".format(d_r1.strftime("%d %b %Y")))
    wh = connect(WAREHOUSE, "warehouse")
    touched = []
    try:
        with wh:
            with wh.cursor() as cur:
                for user in RECIPIENTS:
                    tid = "dst_{0}_daily_sales_track".format(user)
                    cur.execute("SELECT id, version_level FROM tech_team_outputs.ph_task "
                                "WHERE task_id = %s", (tid,))
                    found = cur.fetchall()
                    if len(found) > 1:
                        raise RuntimeError("task_id {0} matches {1} rows".format(tid, len(found)))
                    if found:
                        cur.execute(
                            "UPDATE tech_team_outputs.ph_task SET html_content=%s, task_name=%s, "
                            "assigned_user_team=%s, version_level=%s, version_status='released', "
                            "updated_at=now() WHERE id=%s",
                            (html, task_name, AUDIENCE, found[0][1] + 1, found[0][0]))
                        log("  updated id={0} v{1} {2}".format(found[0][0], found[0][1] + 1, tid))
                        touched.append(found[0][0])
                    else:
                        cur.execute(
                            "INSERT INTO tech_team_outputs.ph_task (project_name, project_code, "
                            "task_name, task_id, team, developer, assigned_user, "
                            "assigned_user_team, html_content, phase_level, version_level, "
                            "version_status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
                            "RETURNING id",
                            ("Daily Sales Track", "dst", task_name, tid, "Development", "Abiraj",
                             user, AUDIENCE, html, 1, 1, "released"))
                        rid = cur.fetchone()[0]
                        touched.append(rid)
                        log("  inserted id={0} {1}".format(rid, tid))

                # Read every payload back and verify it BEFORE the commit. A truncated or
                # mangled write is otherwise invisible until a human opens the portal.
                bad = []
                for rid in touched:
                    cur.execute("SELECT md5(html_content), assigned_user_team "
                                "FROM tech_team_outputs.ph_task WHERE id = %s", (rid,))
                    stored_md5, team_tag = cur.fetchone()
                    if stored_md5 != html_md5:
                        bad.append("id={0} md5".format(rid))
                    if team_tag != AUDIENCE:
                        bad.append("id={0} routing={1}".format(rid, team_tag))
                if bad:
                    raise RuntimeError(
                        "pre-commit verify FAILED ({0}) - rolling back, nothing published".format(
                            ", ".join(bad)))
                log("  verified {0} payloads md5={1}, routing {2} intact".format(
                    len(touched), html_md5[:8], AUDIENCE))
    finally:
        wh.close()

    json.dump({"rows": len(rows), "orders": sum(r["o_r1"] for r in rows),
               "date": d_r1.isoformat()},
              io.open(LAST_GOOD, "w", encoding="utf-8"))
    status("OK", "{0} rows | {1} | md5 {2} | published to {3} users".format(
        len(rows),
        " · ".join("{0} {1:,.2f}".format(k, v) for k, v in sorted(
            {r["currency"]: sum(x["s_r1"] for x in rows if x["currency"] == r["currency"])
             for r in rows}.items())),
        html_md5[:8], len(RECIPIENTS)))
    log("done")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                    # noqa: BLE001 - must always fail closed
        log("STATUS FAILED | {0}".format(exc))
        log(traceback.format_exc().strip().replace("\n", " | "))
        log("previous report left live and untouched")
        sys.exit(1)
