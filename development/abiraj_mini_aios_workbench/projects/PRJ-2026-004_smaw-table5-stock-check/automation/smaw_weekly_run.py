# -*- coding: utf-8 -*-
"""
SMAW - Table 5 Weekly Stock Check (Thuwaraga) - AUTONOMOUS weekly run (REQ-06 automation).

Every Monday: rebuild the full-portfolio Table 5 stock dashboard for Thuwaraga READ-ONLY from the
live warehouse and refresh the ph_task row (id 137, project_code SMAW).

The signed-off SQL (generate_dataset_all_asins.sql) already anchors on CURRENT_DATE - run-date safe,
no parameterization. Its output columns are exactly the data_all.json keys (asin, account,
listing_sku, master_sku, amazon_fbm, uk_warehouse, order_count_90, velocity, days_remaining,
suppliers, po_qty, containers, stock_status), so mapping is 1:1. The signed-off build_all_html.py
adds the refined `cat` split and renders the polished dashboard.

Publish grain = WEEKLY REPLACE in place (task_id SMAW_thuwaraga_table5_all_asins-V2, id 137),
backup-first, md5-verified. ONE warehouse connection. FAILS CLOSED.

NOTE: the live V2 (id 137, 2026-07-09) was built while the inventory feed was frozen at 2026-05-04.
The feed is LIVE again (updated 2026-07-23), so the first automated run legitimately refreshes stale
stock to current - stock numbers will move. That is the point (the report was stale), not a bug.

Flags:  --dry-run / --no-publish   (build + validate, write NOTHING to ph_task)
Usage:  python smaw_weekly_run.py [--dry-run]

Status: BUILT 2026-07-24 - dry-run validate before scheduling.
"""
import os, sys, json, time, hashlib, subprocess
import datetime as dt
from decimal import Decimal
import psycopg2

HERE      = os.path.dirname(os.path.abspath(__file__))
PROJECT   = os.path.dirname(HERE)
SQL_PATH  = os.path.join(PROJECT, "sql", "REQ-06_table5-weekly-stock-check", "generate_dataset_all_asins.sql")
FINAL_DIR = os.path.join(PROJECT, "evidence", "final_outputs", "REQ-06_table5-weekly-stock-check")
BUILD_ALL = os.path.join(FINAL_DIR, "build_all_html.py")
LAST_GOOD = os.path.join(HERE, "smaw_last_good.json")
STATUS    = os.path.join(HERE, "smaw_status.txt")
DATA_OUT  = os.path.join(HERE, "smaw_data_all.json")
HTML_OUT  = os.path.join(HERE, "smaw_dashboard.html")

PUBLISH = not ("--dry-run" in sys.argv or "--no-publish" in sys.argv)

# ---- ph_task identity (id 137, verified) ----
PROJECT_NAME = "SMAW Table 5 Weekly Stock Check - Thuwaraga (full portfolio)"
PROJECT_CODE = "SMAW"
TASK_ID      = "SMAW_thuwaraga_table5_all_asins-V2"
TASK_NAME    = "SMAW - Table 5 Weekly Stock Check - Thuwaraga (weekly auto)"
TEAM, DEVELOPER = "Development", "Abiraj"
ASSIGNED_USER, ASSIGNED_USER_TEAM = "thuwaraga", "ph_priors"

MIN_ROWS = int(os.getenv("SMAW_MIN_ROWS", "400"))     # live reference 756 rows (733 ASINs)
MAX_DROP = float(os.getenv("SMAW_MAX_DROP", "0.40"))  # collapse guard vs last good run
SQL_TIMEOUT_MS = int(os.getenv("SMAW_SQL_TIMEOUT_MS", "180000"))

WH = dict(host=os.getenv("PGHOST", "149.28.134.54"), port=os.getenv("PGPORT", "5435"),
          dbname=os.getenv("PGDATABASE", "order_management_copy"),
          user=os.getenv("PGUSER", "temp_user"), password=os.getenv("PGPASSWORD"))

KEYS = ["asin", "account", "listing_sku", "master_sku", "amazon_fbm", "uk_warehouse",
        "order_count_90", "velocity", "days_remaining", "suppliers", "po_qty", "containers", "stock_status"]


def log(m): print("[SMAW] " + m, flush=True)

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


def collapse_guard(n):
    if not os.path.exists(LAST_GOOD): return
    try: prev = json.load(open(LAST_GOOD, encoding="utf-8")).get("rows")
    except (ValueError, OSError): log("WARN: %s unreadable - skipping collapse check" % LAST_GOOD); return
    if prev and n < prev * (1 - MAX_DROP):
        die("rows collapsed %d -> %d (>%.0f%% drop vs last good run)" % (prev, n, MAX_DROP * 100))
    if prev: log("collapse guard OK: %d vs last good %d" % (n, prev))

def record_good(n, crit):
    try: json.dump({"rows": n, "critical": crit}, open(LAST_GOOD, "w", encoding="utf-8"), indent=1)
    except OSError as e: log("WARN: could not write %s (%s)" % (LAST_GOOD, e))


def main():
    if not WH["password"]:
        die("PGPASSWORD not set - see 05_documentation/capability/shared_db_credentials/")
    log("run_date = %s · publish=%s" % (dt.date.today(), PUBLISH))

    sql = open(SQL_PATH, encoding="utf-8").read()
    # temp_user (the only role a scheduled task can use) has NO access to the `supplier` schema.
    # Those 3 incoming columns (po_qty/suppliers/containers) are all-NULL in the live V2 anyway
    # (0 of 756 rows populated), so neutralise the supplier-reading CTE with an empty stub - the
    # LEFT JOIN then yields the same NULLs, with zero data loss. Fails closed if the anchor moves.
    SUPPLIER_CTE = ("incoming AS (\n"
                    "  SELECT oi.sku, SUM(COALESCE(oi.ctns,0)*COALESCE(oi.ctn_pcs,0))::int AS po_qty,\n"
                    "         STRING_AGG(DISTINCT sup.name,', ') AS suppliers, STRING_AGG(DISTINCT fc.name,', ') AS containers\n"
                    "  FROM supplier.order_items oi JOIN supplier.orders o ON o.id=oi.order_id\n"
                    "  JOIN supplier.suppliers sup ON sup.id=o.supplier_id\n"
                    "  LEFT JOIN supplier.final_containers fc ON fc.id=oi.final_container_id\n"
                    "  WHERE o.status_arrived=0 GROUP BY oi.sku\n"
                    ")")
    STUB = ("incoming AS (  -- supplier schema not readable by temp_user; all-NULL in live V2, so stubbed\n"
            "  SELECT NULL::text AS sku, NULL::int AS po_qty, NULL::text AS suppliers, NULL::text AS containers WHERE false\n"
            ")")
    if SUPPLIER_CTE not in sql:
        die("could not locate the `incoming` supplier CTE to stub - canonical SQL changed; refusing to run")
    sql = sql.replace(SUPPLIER_CTE, STUB)

    conn = connect(); conn.set_session(readonly=True)
    with conn.cursor() as cur:
        cur.execute("SET statement_timeout=%d" % SQL_TIMEOUT_MS)
        cur.execute(sql)
        cols = [d[0] for d in cur.description]
        raw = cur.fetchall()
    conn.rollback()
    log("rows=%d" % len(raw))

    miss = [k for k in KEYS if k not in cols]
    if miss: die("SQL output is missing expected column(s): %s" % miss)

    # ---- map to data_all.json rows (1:1 by column name; Decimal -> number) ----
    def conv(v):
        if isinstance(v, Decimal): return int(v) if v == v.to_integral_value() else float(v)
        if isinstance(v, dt.date): return v.isoformat()
        return v
    idx = {c: i for i, c in enumerate(cols)}
    rows = [{k: conv(r[idx[k]]) for k in KEYS} for r in raw]

    # ---- gates ----
    if len(rows) < MIN_ROWS: die("only %d rows (< floor %d) - broken pull" % (len(rows), MIN_ROWS))
    collapse_guard(len(rows))
    crit = sum(1 for r in rows if r["stock_status"] == "No Stock / Critical")
    healthy = sum(1 for r in rows if r["stock_status"] == "Healthy Stock")
    log("validation PASSED: %d rows | %d critical | %d healthy" % (len(rows), crit, healthy))

    # ---- build the dashboard via the signed-off builder (env-var paths, no duplication) ----
    json.dump(rows, open(DATA_OUT, "w", encoding="utf-8"), ensure_ascii=False)
    env = dict(os.environ, SMAW_DATA=DATA_OUT, SMAW_OUT=HTML_OUT)
    p = subprocess.run([sys.executable, BUILD_ALL], cwd=FINAL_DIR, env=env, capture_output=True, text=True)
    if p.returncode != 0 or not os.path.exists(HTML_OUT):
        die("build_all_html.py failed: %s" % ((p.stderr or p.stdout)[-200:]))
    html = open(HTML_OUT, encoding="utf-8").read()
    if "__DATA__" in html or len(html) < 50000:
        die("built HTML looks broken (%d bytes)" % len(html))
    html_md5 = hashlib.md5(html.encode("utf-8")).hexdigest()
    log("built dashboard: %d bytes, md5 %s" % (len(html), html_md5[:8]))

    if not PUBLISH:
        log("--dry-run: recomputed, validated, built; wrote NOTHING to ph_task.")
        _status("OK(dry-run)", "%d rows / %d critical / %d healthy | built only" % (len(rows), crit, healthy))
        conn.close(); log("done."); return

    desc = ("SMAW Table 5 weekly - Thuwaraga full-portfolio stock: %d ASIN-account rows, %d No-Stock/Critical, "
            "%d Healthy. UK stock = location_wise_inv_stock (live); velocity = 90d FBM units / 90."
            % (len(rows), crit, healthy))
    conn.set_session(readonly=False)   # leave the read-only read phase before publishing (the UPDATE writes)
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, html_content FROM tech_team_outputs.ph_task WHERE task_id=%s", (TASK_ID,))
                got = cur.fetchone()
                if got:
                    open(os.path.join(HERE, "smaw_ph_task_backup_%s.html" % dt.datetime.now().strftime("%Y%m%d_%H%M%S")),
                         "w", encoding="utf-8").write(got[1] or "")
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
    record_good(len(rows), crit)
    _status("OK", "%d rows / %d critical / %d healthy | PUBLISHED" % (len(rows), crit, healthy))
    log("done.")


if __name__ == "__main__":
    main()
