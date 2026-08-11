"""
chop_monthly_run.py — Channel Opportunity (chop / PRJ-2026-021) fleet-standard monthly run.

Replaces the frozen 2026-08-05 JSON snapshot with a LIVE pull from the raw ledsone DB
(order_management), reuses the existing build_chop_d01 classifier + renderer, validates with
fail-closed gates, and publishes the single DE dashboard row to tech_team_outputs.ph_task via a
guarded, md5-verified UPSERT (stable task_id -> refresh in place, never duplicate).

  python chop_monthly_run.py             # real run: pull + build + publish
  python chop_monthly_run.py --dry-run   # pull + build + validate, publish NOTHING

Credentials (env only, never hardcoded):
  Live source  : LED_PGHOST/PORT/DATABASE/USER + LED_PGPASSWORD   (raw ledsone, order_management)
  Publish target: PGHOST/PORT/DATABASE/USER   + PGPASSWORD        (warehouse, tech_team_outputs.ph_task)

Business note: the winner/weak/missing thresholds are DOCUMENTED DEFAULTS (FLOOR=10, Shopify>=50%,
Marketplace>=60%/<=20%), owner-pending Mahima. They live in build_chop_d01 and are reused verbatim.
"""
import os, sys, time, json, hashlib, logging, tempfile
from datetime import date, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
SQL_DIR = os.path.abspath(os.path.join(HERE, "..", "sql", "REQ-24_channel-opportunity"))
sys.path.insert(0, SQL_DIR)
import build_chop_d01 as chop   # reuse classify() + build() + write_dashboard()

PROJECT_CODE = "chop"
PROJECT_NAME = "Channel Opportunity"
TASK_NAME    = "Channel Opportunity — cross-channel listing-gap finder (Shopify/Amazon/eBay, DE)"
TASK_ID      = "chop_channel_opportunity_DE-V1"     # STABLE -> upsert in place, never duplicate
TEAM, DEVELOPER, TEAM_TAG = "Development", "Abiraj", "german_priors"
ASSIGNED_USER = "Mahi"

MIN_BASE_SKUS = 1500     # floor: a real pull returns ~2.4k DE base SKUs
MIN_OPPS      = 100      # floor: ~283 opportunity rows in a healthy window
WINDOW_DAYS   = 90

LED = {"host": os.getenv("LED_PGHOST", "169.58.91.229"),
       "port": os.getenv("LED_PGPORT", "5432"),
       "dbname": os.getenv("LED_PGDATABASE", "ledsone"),
       "user": os.getenv("LED_PGUSER", "dev_user"),
       "password": os.getenv("LED_PGPASSWORD")}
WH = {"host": os.getenv("PGHOST", "149.28.134.54"),
      "port": os.getenv("PGPORT", "5435"),
      "dbname": os.getenv("PGDATABASE", "order_management_copy"),
      "user": os.getenv("PGUSER", "temp_user"),
      "password": os.getenv("PGPASSWORD")}

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-7s %(message)s")
log = logging.getLogger("chop")


def die(code, msg):
    log.error("ABORT (exit %s): %s", code, msg)
    log.error("NOTHING WAS PUBLISHED.")
    sys.exit(code)


PIVOT_SQL = """
WITH lines AS (
  SELECT regexp_replace(COALESCE(NULLIF(oii.real_sku,''), oii.item_sku), '-IDE$', '') AS sku,
         src.source_name,
         SUM(oii.item_quantity::numeric) AS units
  FROM order_management.orders o
  JOIN order_management.sub_source ss ON ss.id = o.sub_source_id
  JOIN order_management.source src ON src.id = ss.source_id
  JOIN order_management.order_item_info oii ON oii.order_id = o.id
  WHERE o.status='Completed' AND o.market_place='10'
    AND o.order_date >= (CURRENT_DATE - INTERVAL '%d days') AND o.order_date < CURRENT_DATE
    AND src.source_name IN ('AMAZON','EBAY','SHOPIFY')
    AND COALESCE(NULLIF(oii.real_sku,''), oii.item_sku) <> ''
  GROUP BY 1,2
)
SELECT sku,
  COALESCE(SUM(units) FILTER (WHERE source_name='SHOPIFY'),0)::int AS shopify_u,
  COALESCE(SUM(units) FILTER (WHERE source_name='AMAZON'),0)::int  AS amazon_u,
  COALESCE(SUM(units) FILTER (WHERE source_name='EBAY'),0)::int    AS ebay_u,
  SUM(units)::int AS total_u
FROM lines GROUP BY sku
""" % WINDOW_DAYS


def connect(cfg, label):
    import psycopg2
    for attempt in range(1, 6):
        try:
            return psycopg2.connect(connect_timeout=20, **cfg)
        except Exception as e:
            log.warning("%s connect attempt %d/5 failed: %s", label, attempt, str(e).splitlines()[0])
            if attempt < 5:
                time.sleep(8)
    die(1, f"could not connect to {label} after 5 attempts")


def pull_live():
    if not LED["password"]:
        die(1, "LED_PGPASSWORD not set")
    conn = connect(LED, "ledsone"); conn.set_session(readonly=True)
    with conn.cursor() as cur:
        cur.execute(PIVOT_SQL)
        rows = [{"sku": r[0], "shopify_u": r[1], "amazon_u": r[2], "ebay_u": r[3], "total_u": r[4]}
                for r in cur.fetchall()]
    conn.close()
    return rows


def main():
    dry = "--dry-run" in sys.argv
    today = date.today()
    through = (today - timedelta(days=1)).isoformat()
    log.info("Channel Opportunity run | dry_run=%s | window=%dd through %s", dry, WINDOW_DAYS, through)

    rows = pull_live()
    if len(rows) < MIN_BASE_SKUS:
        die(2, f"only {len(rows)} base SKUs (< floor {MIN_BASE_SKUS}) - broken pull")
    log.info("Pulled %d base SKUs / %d units", len(rows), sum(r["total_u"] for r in rows))

    # ---- reuse the governed classifier + renderer, sourced from the LIVE rows ----
    raw_path = os.path.join(tempfile.gettempdir(), f"chop_live_{today.isoformat()}.json")
    json.dump({"data": {"rows": rows}}, open(raw_path, "w", encoding="utf-8"))
    chop.RAW = raw_path
    chop.SNAP = os.path.join(SQL_DIR, f"chop_payload_{today.isoformat()}.json")  # do NOT clobber the Aug-5 snapshot
    chop.DATA_THROUGH = through
    chop.build()   # writes OUT_XLSX + OUT_HTML from the live rows

    opps = sum(1 for r in rows if chop.classify(r["shopify_u"], r["amazon_u"], r["ebay_u"])[0])
    if opps < MIN_OPPS:
        die(2, f"only {opps} opportunity rows (< floor {MIN_OPPS}) - refusing to publish a thin report")
    log.info("Classified %d opportunity rows", opps)

    html = open(chop.OUT_HTML, encoding="utf-8").read()
    md5 = hashlib.md5(html.encode("utf-8")).hexdigest()
    if "<table" not in html or len(html) < 10000:
        die(2, f"assembly looks broken ({len(html)} bytes)")

    if dry:
        log.info("DRY-RUN: built %d-byte dashboard (md5 %s), validated - wrote NOTHING to ph_task.", len(html), md5[:8])
        return

    # ---- guarded UPSERT publish (one txn, md5-verified) ----
    if not WH["password"]:
        die(1, "PGPASSWORD not set (publish target)")
    conn = connect(WH, "warehouse")
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""UPDATE tech_team_outputs.ph_task
                               SET html_content=%s, task_name=%s, version_level=version_level+1, updated_at=now()
                               WHERE project_code=%s AND task_id=%s RETURNING id""",
                            (html, TASK_NAME, PROJECT_CODE, TASK_ID))
                got = cur.fetchall()
                if len(got) == 1:
                    rid, how = got[0][0], "UPDATE"
                elif len(got) == 0:
                    cur.execute("""INSERT INTO tech_team_outputs.ph_task
                        (project_name,project_code,task_name,task_id,team,developer,
                         assigned_user,assigned_user_team,html_content,description,
                         phase_level,version_level,version_status)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,'',1,1,'released') RETURNING id""",
                        (PROJECT_NAME, PROJECT_CODE, TASK_NAME, TASK_ID, TEAM, DEVELOPER,
                         ASSIGNED_USER, TEAM_TAG, html))
                    rid, how = cur.fetchone()[0], "INSERT (new)"
                else:
                    raise RuntimeError(f"task_id {TASK_ID} matched {len(got)} rows - aborting")
                cur.execute("SELECT md5(html_content) FROM tech_team_outputs.ph_task WHERE id=%s", (rid,))
                if cur.fetchone()[0] != md5:
                    raise RuntimeError("md5 verify failed pre-commit - rolling back")
        log.info("PUBLISHED + COMMITTED: %s id=%s md5=%s", how, rid, md5[:8])
    finally:
        conn.close()

    # post-publish verify (only the row we just wrote)
    conn = connect(WH, "warehouse"); conn.set_session(readonly=True)
    with conn.cursor() as cur:
        cur.execute("""SELECT assigned_user_team, version_status FROM tech_team_outputs.ph_task
                       WHERE project_code=%s AND task_id=%s""", (PROJECT_CODE, TASK_ID))
        tag, st = cur.fetchone()
    conn.close()
    if tag != TEAM_TAG or st not in ("released", "completed"):
        die(4, f"post-publish verify failed: team={tag} status={st}")
    log.info("Post-publish verify OK. Run complete.")


if __name__ == "__main__":
    main()
