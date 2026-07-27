# -*- coding: utf-8 -*-
"""
ZSFO - Zero Sales Full Optimization (Utharsika) - AUTONOMOUS weekly run (REQ-08 automation).

Every Monday: recompute Utharsika's Amazon-UK ASINs with ZERO units sold in the last completed
30 days (FBA+FBM AND vendor/1P), plus the traffic-funnel + stock diagnostics, READ-ONLY from the
live warehouse, and refresh the dashboard in tech_team_outputs.ph_task.

Window (owner rule): [run_date-30, run_date-1], current day excluded. run_date defaults to today
(the Monday it runs). The signed-off canonical SQL hardcodes a run_date + five weekly traffic
buckets; this runner computes all of them from run_date and substitutes the literals - the one
"scheduling not wired" gap noted in SYSTEM_REFERENCE.

Publish grain = WEEKLY REPLACE in place (task_id ZSFO_utharsika_zero_sales_dashboard-V1), matching
the other weekly jobs (T7/EPC/EPPA/DST) and how ZSFO was first published (id 167). Backup-first,
md5-verified.

ONE database: warehouse temp_user = data source (public.*, read-only) + publish target (ph_task).
FAILS CLOSED: gates run before any write. Any failure -> exit 2, nothing published.

Flags:  --dry-run / --no-publish  (build + validate, write NOTHING to ph_task)
        --date YYYY-MM-DD         (override run_date; use 2026-07-10 to reproduce the reference)
Usage:  python zsfo_weekly_run.py [--dry-run] [--date YYYY-MM-DD]

Status: BUILT 2026-07-24 - validate with --date 2026-07-10 (must give 1,719 universe / 1,250 zero).
"""
import os, sys, json, time, hashlib, subprocess
import datetime as dt
from decimal import Decimal
import psycopg2

HERE      = os.path.dirname(os.path.abspath(__file__))
PROJECT   = os.path.dirname(HERE)
SQL_PATH  = os.path.join(PROJECT, "sql", "REQ-08_zero-sales-full-optimization", "generate_dataset.sql")
FINAL_DIR = os.path.join(PROJECT, "evidence", "final_outputs", "REQ-08_zero-sales-full-optimization")
BUILD_HTML= os.path.join(FINAL_DIR, "build_html.py")
LAST_GOOD = os.path.join(HERE, "zsfo_last_good.json")
STATUS    = os.path.join(HERE, "zsfo_status.txt")
DATA_OUT  = os.path.join(HERE, "zsfo_data.json")
HTML_OUT  = os.path.join(HERE, "zsfo_dashboard.html")

PUBLISH  = not ("--dry-run" in sys.argv or "--no-publish" in sys.argv)
DATE_ARG = None
if "--date" in sys.argv:
    try: DATE_ARG = sys.argv[sys.argv.index("--date") + 1]
    except IndexError: pass

# ---- ph_task identity (from PROJECT_HOME id 167) ----
PROJECT_NAME = "Zero Sales Full Optimization (ZSFO) - Utharsika Amazon UK"
PROJECT_CODE = "ZSFO"
TASK_ID      = "ZSFO_utharsika_zero_sales_dashboard-V1"
TASK_NAME    = "ZSFO - Zero Sales Full Optimization - Utharsika (weekly auto)"
TEAM, DEVELOPER = "Development", "Abiraj"
ASSIGNED_USER, ASSIGNED_USER_TEAM = "utharsika", "ph_priors"

# ---- gates ----
MIN_UNIVERSE = int(os.getenv("ZSFO_MIN_UNIVERSE", "800"))   # live reference universe 1,719
MIN_ZERO     = int(os.getenv("ZSFO_MIN_ZERO", "1"))         # never publish 0 rows over a good report
MAX_DROP     = float(os.getenv("ZSFO_MAX_DROP", "0.40"))    # collapse guard vs last good run
SQL_TIMEOUT_MS = int(os.getenv("ZSFO_SQL_TIMEOUT_MS", "180000"))

WH = dict(host=os.getenv("PGHOST", "149.28.134.54"), port=os.getenv("PGPORT", "5435"),
          dbname=os.getenv("PGDATABASE", "order_management_copy"),
          user=os.getenv("PGUSER", "temp_user"), password=os.getenv("PGPASSWORD"))

# SQL friendly column -> data.json short key ("Last Month Sales" is always 0, not carried)
COLMAP = {
    "ASIN": "asin", "SKU": "sku", "Local UK Warehouse stock": "uk_stock",
    "Amazon FBM Stock": "fbm_stock", "Impressions": "impr", "Clicks": "clk",
    "Conversion Rate": "cr", "Last Amazon Sale (lifetime)": "last_order",
    "Last Vendor Sale (lifetime)": "last_vendor", "Vendor Units (lifetime)": "vlife",
    "W1 Impr": "w1i", "W1 Clk": "w1c", "W2 Impr": "w2i", "W2 Clk": "w2c",
    "W3 Impr": "w3i", "W3 Clk": "w3c", "W4 Impr": "w4i", "W4 Clk": "w4c",
    "W5 Impr": "w5i", "W5 Clk": "w5c", "Root-cause hint": "root_cause",
}


def log(m): print("[ZSFO] " + m, flush=True)

def _status(state, msg):
    try:
        with open(STATUS, "a", encoding="utf-8") as f:
            f.write("[%s]  %s  |  %s\n" % (dt.datetime.now().strftime("%Y-%m-%d %H:%M"), state, msg))
    except Exception:
        pass

def die(msg):
    log("ABORT: %s  -> nothing published" % msg)
    _status("FAILED", msg)
    sys.exit(2)


def connect():
    last = None
    for attempt in range(1, 6):
        try:
            c = psycopg2.connect(connect_timeout=20, **WH); c.set_client_encoding("UTF8"); return c
        except Exception as e:
            last = str(e).strip().splitlines()[-1]
            log("  warehouse connect attempt %d/5 failed: %s" % (attempt, last)); time.sleep(8)
    die("cannot connect to the warehouse after 5 attempts: %s" % last)


# ---------------------------------------------------------------- window / parameterize
REF = {  # the literal dates in the signed-off SQL (run_date 2026-07-10) -> recomputed per run
    "run": dt.date(2026, 7, 10), "ws": dt.date(2026, 6, 10), "we": dt.date(2026, 7, 9),
    "buckets": [(dt.date(2026, 6, 10), dt.date(2026, 6, 16)), (dt.date(2026, 6, 17), dt.date(2026, 6, 23)),
                (dt.date(2026, 6, 24), dt.date(2026, 6, 30)), (dt.date(2026, 7, 1), dt.date(2026, 7, 7)),
                (dt.date(2026, 7, 8), dt.date(2026, 7, 9))],
}

def window(run_date):
    ws = run_date - dt.timedelta(days=30)
    we = run_date - dt.timedelta(days=1)
    b = [(ws, ws + dt.timedelta(days=6)), (ws + dt.timedelta(days=7),  ws + dt.timedelta(days=13)),
         (ws + dt.timedelta(days=14), ws + dt.timedelta(days=20)), (ws + dt.timedelta(days=21), ws + dt.timedelta(days=27)),
         (ws + dt.timedelta(days=28), we)]
    return ws, we, b

def parameterize(sql, run_date):
    """Replace the signed-off SQL's hardcoded run_date + 5 bucket date literals with this run's."""
    ws, we, buckets = window(run_date)
    subs = {"DATE '%s'" % REF["run"].isoformat(): "DATE '%s'" % run_date.isoformat()}
    for (os_, oe), (ns, ne) in zip(REF["buckets"], buckets):
        subs["DATE '%s'" % os_.isoformat()] = "DATE '%s'" % ns.isoformat()
        subs["DATE '%s'" % oe.isoformat()] = "DATE '%s'" % ne.isoformat()
    for old, new in subs.items():
        if old not in sql:
            die("expected date literal %s missing from the canonical SQL - cannot parameterize safely" % old)
        sql = sql.replace(old, new)
    # guard: no reference literal must survive (would silently report the wrong week)
    for d in (REF["run"], REF["ws"], REF["we"]):
        if run_date != REF["run"] and "DATE '%s'" % d.isoformat() in sql:
            die("a reference date %s survived substitution - refusing to run the wrong window" % d)
    return sql, ws, we, buckets


def bucket_labels(buckets):
    return ["%02d-%02d %s" % (s.day, e.day, e.strftime("%b")) for s, e in buckets]


# ---------------------------------------------------------------- collapse guard
def collapse_guard(n):
    if not os.path.exists(LAST_GOOD): return
    try: prev = json.load(open(LAST_GOOD, encoding="utf-8")).get("zero")
    except (ValueError, OSError): log("WARN: %s unreadable - skipping collapse check" % LAST_GOOD); return
    if prev and n < prev * (1 - MAX_DROP):
        die("zero-sale rows collapsed %d -> %d (>%.0f%% drop vs last good run)" % (prev, n, MAX_DROP * 100))
    if prev: log("collapse guard OK: %d vs last good %d" % (n, prev))

def record_good(universe, zero):
    try: json.dump({"universe": universe, "zero": zero}, open(LAST_GOOD, "w", encoding="utf-8"), indent=1)
    except OSError as e: log("WARN: could not write %s (%s)" % (LAST_GOOD, e))


# ---------------------------------------------------------------- main
def main():
    if not WH["password"]:
        die("PGPASSWORD not set - see 05_documentation/capability/shared_db_credentials/")
    run_date = dt.date.fromisoformat(DATE_ARG) if DATE_ARG else dt.date.today()
    log("run_date = %s · publish=%s" % (run_date, PUBLISH))

    sql = open(SQL_PATH, encoding="utf-8").read()
    sql, ws, we, buckets = parameterize(sql, run_date)
    log("window: %s .. %s | buckets %s" % (ws, we, bucket_labels(buckets)))

    conn = connect(); conn.set_session(readonly=True)
    with conn.cursor() as cur:
        cur.execute("SET statement_timeout=%d" % SQL_TIMEOUT_MS)
        cur.execute("""SELECT count(DISTINCT ref_id) FROM public.traffic_data
                       WHERE which_channel=1 AND market_place='UK' AND user_name='utharsika'""")
        universe = cur.fetchone()[0]
        cur.execute(sql)
        cols = [d[0] for d in cur.description]
        raw = cur.fetchall()
    conn.rollback()
    log("universe=%d · zero-sale rows=%d" % (universe, len(raw)))

    # ---- map to data.json rows ----
    rows = []
    for r in raw:
        d = dict(zip(cols, r))
        row = {}
        for friendly, key in COLMAP.items():
            v = d.get(friendly)
            if key in ("last_order", "last_vendor"):
                v = v.isoformat() if isinstance(v, dt.date) else None
            elif key == "cr":
                v = float(v) if v is not None else 0.0
            elif isinstance(v, Decimal):                       # stock/impr/clk/units come back Decimal
                v = int(v) if v == v.to_integral_value() else float(v)
            row[key] = v
        rows.append(row)

    # ---- gates (fail closed, before any write) ----
    if universe < MIN_UNIVERSE:  die("universe %d < floor %d - broken pull" % (universe, MIN_UNIVERSE))
    if len(rows) < MIN_ZERO:     die("0 zero-sale rows - refusing to publish an empty report")
    collapse_guard(len(rows))
    # Reference proof (run_date 2026-07-10): the zero-sale ROWS are the deliverable and must
    # reproduce EXACTLY (1,250). The universe is a LIVE distinct-ASIN count that legitimately
    # drifts as ASINs gain/lose traffic (1,719 at capture -> 1,720 on 2026-07-24, +1), so it is
    # a drift check, not equality - same lesson as the EBPD anchor.
    if run_date == REF["run"]:
        if len(rows) != 1250:
            die("reference check failed: %d zero-sale rows, expected exactly 1250" % len(rows))
        if abs(universe - 1719) > max(5, int(1719 * 0.01)):
            die("reference universe drifted too far: %d vs 1719 (>1%%)" % universe)
        log("reference check OK: 1250 zero-sale rows reproduced; universe %d vs 1719 (%+d drift)"
            % (universe, universe - 1719))
    miss = [k for k in ("asin", "uk_stock", "impr", "root_cause") if k not in rows[0]]
    if miss: die("mapped row missing key(s): %s" % miss)
    log("validation PASSED")

    # ---- meta + data.json ----
    meta = {"report": "Zero Sales Full Optimization (ZSFO)", "task_id": TASK_ID, "project_code": PROJECT_CODE,
            "developer": "abiraj", "portfolio_holder": "utharsika", "marketplace": "Amazon UK",
            "run_date": run_date.isoformat(), "window_start": ws.isoformat(), "window_end": we.isoformat(),
            "week_buckets": bucket_labels(buckets), "universe_asins": universe, "zero_sale_rows": len(rows),
            "vendor_logic": "OVERLAP (NOT (end_time < ws OR start_time > we))",
            "listing_bridge": "ref_id + UK + wrong_sku=0 + is_parent=0 (which_channel NULL for utharsika - not filtered)",
            "zero_sale_def": "0 units across order_transaction (FBA+FBM, Completed) AND vendor_sales (1P) in window",
            "conversion_rate": "conversion / clicks",
            "stock_note": "location_wise_inv_stock is live-as-of-today; window is historical",
            "generated_by": "seg-style autonomous weekly runner (direct psycopg2, read-only)"}
    json.dump({"meta": meta, "rows": rows}, open(DATA_OUT, "w", encoding="utf-8"), ensure_ascii=False)

    # ---- build the HTML via the signed-off builder (env-var paths, no duplication) ----
    env = dict(os.environ, ZSFO_DATA=DATA_OUT, ZSFO_OUT=HTML_OUT)
    p = subprocess.run([sys.executable, BUILD_HTML], env=env, capture_output=True, text=True)
    if p.returncode != 0 or not os.path.exists(HTML_OUT):
        die("build_html.py failed: %s" % (p.stderr.strip().splitlines()[-1:] or p.stdout[-200:]))
    html = open(HTML_OUT, encoding="utf-8").read()
    if "<title>" not in html or len(html) < 50000:
        die("built HTML looks broken (%d bytes)" % len(html))
    html_md5 = hashlib.md5(html.encode("utf-8")).hexdigest()
    log("built dashboard: %d bytes, md5 %s" % (len(html), html_md5[:8]))

    if not PUBLISH:
        log("--dry-run: recomputed, validated, built; wrote NOTHING to ph_task.")
        _status("OK(dry-run)", "universe %d / zero %d | %s..%s | built only" % (universe, len(rows), ws, we))
        conn.close(); log("done."); return

    # ---- publish: weekly REPLACE in place, backup-first, md5-verified ----
    desc = ("ZSFO weekly - Utharsika Amazon-UK ASINs with 0 units sold in %s..%s (FBA+FBM AND vendor). "
            "%d zero-sale of %d universe. Traffic funnel + stock diagnostics + root-cause hint."
            % (ws, we, len(rows), universe))
    conn.set_session(readonly=False)   # leave the read-only read phase before publishing (the UPDATE writes)
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, html_content FROM tech_team_outputs.ph_task WHERE task_id=%s", (TASK_ID,))
                got = cur.fetchone()
                if got:
                    bpath = os.path.join(HERE, "zsfo_ph_task_backup_%s.html" % dt.datetime.now().strftime("%Y%m%d_%H%M%S"))
                    open(bpath, "w", encoding="utf-8").write(got[1] or "")
                    cur.execute("""UPDATE tech_team_outputs.ph_task
                                     SET html_content=%s, description=%s, task_name=%s,
                                         version_level=version_level+1, updated_at=now()
                                   WHERE task_id=%s RETURNING id""", (html, desc, TASK_NAME, TASK_ID))
                    rid = cur.fetchone()[0]; how = "UPDATE"
                else:
                    cur.execute("""INSERT INTO tech_team_outputs.ph_task
                        (project_name,project_code,task_name,task_id,team,developer,assigned_user,
                         assigned_user_team,html_content,description,phase_level,version_level,version_status,
                         created_at,updated_at)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,1,1,'released',now(),now()) RETURNING id""",
                        (PROJECT_NAME, PROJECT_CODE, TASK_NAME, TASK_ID, TEAM, DEVELOPER, ASSIGNED_USER,
                         ASSIGNED_USER_TEAM, html, desc)); rid = cur.fetchone()[0]; how = "INSERT"
                cur.execute("SELECT md5(html_content), assigned_user_team FROM tech_team_outputs.ph_task WHERE id=%s", (rid,))
                stored_md5, team = cur.fetchone()
                if stored_md5 != html_md5:      raise RuntimeError("md5 verify failed pre-commit - rolling back")
                if team != ASSIGNED_USER_TEAM:  raise RuntimeError("routing team=%s - rolling back" % team)
                log("  %s id=%s md5=%s team=%s" % (how, rid, html_md5[:8], team))
    except Exception as e:
        die("publish failed, transaction rolled back: %s" % str(e).strip().splitlines()[-1])
    conn.close()
    record_good(universe, len(rows))
    _status("OK", "universe %d / zero %d | %s..%s | PUBLISHED" % (universe, len(rows), ws, we))
    log("done.")


if __name__ == "__main__":
    main()
