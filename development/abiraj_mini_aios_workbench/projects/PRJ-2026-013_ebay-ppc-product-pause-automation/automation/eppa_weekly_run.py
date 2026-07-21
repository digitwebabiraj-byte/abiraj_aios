"""
REQ-15-D02 — eBay PPC Product Pause Automation, autonomous weekly refresh.

Runs every Monday. Pulls the last 30 days live from the `ledsone` database (read-only, direct
psycopg2 — no MCP, because a Scheduled Task has no MCP session), applies the rule engine from
eppa_engine.py, rebuilds the dashboard + workbook, and REFRESHES THE LIVE ph_task ROW so the
portal never shows older numbers than the files on disk.

FAILS CLOSED. If the pull errors, returns no campaigns, or collapses versus the previous run, the
existing outputs are left untouched and the status file records the failure. A stale-but-correct
report is always better than a fresh wrong one that recommends pausing live advertising.

Credentials come from eppa_secrets.bat (git-ignored) via environment variables — never hardcoded.
"""
import os, sys, json, time, runpy, traceback
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, ".."))
SQLDIR = os.path.join(PROJ, "sql", "REQ-15_ebay-ppc-product-pause-automation")
FINAL = os.path.join(PROJ, "evidence", "final_outputs", "REQ-15_ebay-ppc-product-pause-automation")
STATUS = os.path.join(HERE, "eppa_status.json")
LOG = os.path.join(HERE, "eppa_run.log")
sys.path.insert(0, SQLDIR)

# scope — LEDSone eBay UK, Advanced (ON_SITE) Promoted Listings
MARKETPLACE, SUB_SOURCE, CAMPAIGN_TYPE = "EBAY_GB", 1, "ON_SITE"
MIN_CAMPAIGNS = 20          # fail-closed floor: fewer than this means a broken pull, not a quiet week
MAX_DROP = 0.40             # fail-closed: reject a >40% collapse in campaign count vs last good run


def log(msg):
    line = "%s  %s" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg)
    print(line, flush=True)
    try:
        with open(LOG, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except Exception:
        pass


def write_status(ok, msg, extra=None):
    st = dict(ok=ok, message=msg, when=datetime.now(timezone.utc).isoformat(timespec="seconds"))
    if extra:
        st.update(extra)
    try:
        json.dump(st, open(STATUS, "w", encoding="utf-8"), indent=1)
    except Exception:
        pass


SQL_PERF = """
WITH a AS (
  -- ANCHOR = the latest COMPLETE day. MAX(date) is today whenever the hourly sync has already
  -- written, and today is only part-populated (verified 2026-07-21: 8 clicks / GBP 1.39 against a
  -- ~540-click, ~GBP 99 normal day). Anchoring there makes a "30-day" window 29 days plus a stub,
  -- understates every money figure, and could tip a campaign sitting near the ACOS ceiling on
  -- half-counted data. If MAX(date) is in the past it is complete, so use it; otherwise step back.
  SELECT CASE WHEN MAX(date) < CURRENT_DATE THEN MAX(date) ELSE MAX(date) - 1 END AS d
  FROM ebay_campaigns.performance_data),
c AS (
  SELECT campaign_id, campaign_name, campaign_target_type, campaign_status
  FROM ebay_campaigns.campaigns
  WHERE marketplace_id=%(mkt)s AND sub_source=%(ss)s AND deleted=false AND campaign_type=%(ct)s),
p AS (
  SELECT pd.campaign_id,
    SUM(pd.ad_fees_payout_currency)     FILTER (WHERE pd.date > a.d-30) s30,
    SUM(pd.sale_amount_payout_currency) FILTER (WHERE pd.date > a.d-30) sa30,
    SUM(pd.attributed_sales)            FILTER (WHERE pd.date > a.d-30) o30,
    SUM(pd.ad_fees_payout_currency)     FILTER (WHERE pd.date > a.d-7)  s7,
    SUM(pd.sale_amount_payout_currency) FILTER (WHERE pd.date > a.d-7)  sa7,
    SUM(pd.attributed_sales)            FILTER (WHERE pd.date > a.d-14) o14,
    SUM(pd.clicks)                      FILTER (WHERE pd.date > a.d-14) c14,
    SUM(pd.ad_fees_payout_currency)     FILTER (WHERE pd.date > a.d-14) s14
  FROM ebay_campaigns.performance_data pd CROSS JOIN a
  WHERE pd.date > a.d-30 AND pd.date <= a.d GROUP BY 1)
SELECT c.campaign_id::text, c.campaign_name, COALESCE(c.campaign_target_type,'-'),
       c.campaign_status,
       COALESCE(p.s30,0), COALESCE(p.sa30,0), COALESCE(p.o30,0),
       COALESCE(p.s7,0),  COALESCE(p.sa7,0),
       COALESCE(p.o14,0), COALESCE(p.c14,0), COALESCE(p.s14,0),
       (SELECT d FROM a)
FROM c LEFT JOIN p ON p.campaign_id=c.campaign_id;
"""

# Stock position of every listing each campaign advertises.
#   all_list=1  -> mandatory (business/rules/ebay-listing-sku-filter.md); without it, parent
#                  variation containers with no real SKU inflate and corrupt the result.
#   LEFT JOINs  -> a listing with no stock record must survive as "no data", never collapse to 0,
#                  which would trip the stock rule and pause a possibly well-stocked listing.
SQL_STOCK = """
WITH a AS (
  -- ANCHOR = the latest COMPLETE day. MAX(date) is today whenever the hourly sync has already
  -- written, and today is only part-populated (verified 2026-07-21: 8 clicks / GBP 1.39 against a
  -- ~540-click, ~GBP 99 normal day). Anchoring there makes a "30-day" window 29 days plus a stub,
  -- understates every money figure, and could tip a campaign sitting near the ACOS ceiling on
  -- half-counted data. If MAX(date) is in the past it is complete, so use it; otherwise step back.
  SELECT CASE WHEN MAX(date) < CURRENT_DATE THEN MAX(date) ELSE MAX(date) - 1 END AS d
  FROM ebay_campaigns.performance_data),
adv AS (
  SELECT DISTINCT pd.campaign_id, pd.ebay_listing_id::text item_id
  FROM ebay_campaigns.performance_data pd CROSS JOIN a
  JOIN ebay_campaigns.campaigns c ON c.campaign_id=pd.campaign_id
  WHERE c.marketplace_id=%(mkt)s AND c.sub_source=%(ss)s AND c.deleted=false
    AND c.campaign_type=%(ct)s AND pd.date > a.d-30 AND pd.date <= a.d),
ls AS (
  SELECT adv.campaign_id, adv.item_id,
         SUM(COALESCE(x.units,0)) units, COUNT(el.id) skus
  FROM adv
  LEFT JOIN listings.ebay_listings el
    ON el.item_id=adv.item_id AND el.all_list=1 AND el.sub_source=%(ss)s
   AND COALESCE(el.wrong_sku,0)=0
  LEFT JOIN LATERAL (
    SELECT SUM(COALESCE(l.stock,0)) units
    FROM inventory.products pr
    LEFT JOIN inventory.local_inventory_current_stock_location_wise l
      ON l.inventory_id=pr.id AND l.warehouse_location='UK'
    WHERE pr.sku=el.sku) x ON TRUE
  GROUP BY 1,2)
SELECT campaign_id::text, COUNT(*),
       COUNT(*) FILTER (WHERE skus=0),
       COUNT(*) FILTER (WHERE skus>0 AND units=0),
       COUNT(*) FILTER (WHERE skus>0 AND units>0 AND units<%(floor)s)
FROM ls GROUP BY 1;
"""


def main():
    import psycopg2
    from eppa_engine import THRESHOLDS, decide_all

    for var in ("LED_PGHOST", "LED_PGDATABASE", "LED_PGUSER", "LED_PGPASSWORD"):
        if not os.environ.get(var):
            raise RuntimeError("missing credential env var %s — is eppa_secrets.bat filled in?" % var)

    args = dict(mkt=MARKETPLACE, ss=SUB_SOURCE, ct=CAMPAIGN_TYPE, floor=THRESHOLDS["stock_floor"])
    # retry a transient full pool rather than failing the whole run on one bad moment
    wait, conn = 10, None
    for attempt in range(1, 6):
        try:
            conn = psycopg2.connect(
                host=os.environ["LED_PGHOST"], port=os.environ.get("LED_PGPORT", "5432"),
                dbname=os.environ["LED_PGDATABASE"], user=os.environ["LED_PGUSER"],
                password=os.environ["LED_PGPASSWORD"], connect_timeout=30,
                options="-c statement_timeout=300000", application_name="eppa_weekly")
            break
        except psycopg2.OperationalError as exc:
            if attempt == 5 or not any(x in str(exc) for x in (
                    "remaining connection slots", "too many clients",
                    "server closed the connection unexpectedly")):
                raise
            log("ledsone connect attempt %d/5 failed — retrying in %ds" % (attempt, wait))
            time.sleep(wait); wait *= 2
    conn.set_session(readonly=True, autocommit=True)   # belt and braces — this job never writes
    try:
        with conn.cursor() as cur:
            cur.execute(SQL_PERF, args)
            perf = cur.fetchall()
            cur.execute(SQL_STOCK, args)
            stock = {r[0]: dict(total=r[1], nodata=r[2], oos=r[3], low=r[4]) for r in cur.fetchall()}
    finally:
        conn.close()

    if not perf:
        raise RuntimeError("pull returned 0 campaigns")
    anchor = str(perf[0][12])[:10]

    rows = []
    for (cid, name, ttype, cstatus, s30, sa30, o30, s7, sa7, o14, c14, s14, _d) in perf:
        st = stock.get(cid, dict(total=0, nodata=0, oos=0, low=0))
        rows.append(dict(
            campaign_id=cid, campaign=name,
            type=ttype.title() if ttype != "-" else "-", status=cstatus,
            listings=st["total"], no_stock_data=st["nodata"],
            out_of_stock=st["oos"], low_stock=st["low"],
            spend30=float(s30), sales30=float(sa30), ord30=float(o30),
            spend7=float(s7), sales7=float(sa7),
            ord14=float(o14), clicks14=float(c14), spend14=float(s14)))

    # ---- fail-closed gates, BEFORE anything on disk is touched -------------------------------
    if len(rows) < MIN_CAMPAIGNS:
        raise RuntimeError("only %d campaigns returned (floor %d) — refusing to overwrite"
                           % (len(rows), MIN_CAMPAIGNS))
    prev_path = os.path.join(FINAL, "eppa_d01_data.json")
    if os.path.exists(prev_path):
        try:
            prev = json.load(open(prev_path, encoding="utf-8"))["kpis"]["scope"]
            if prev and len(rows) < prev * (1 - MAX_DROP):
                raise RuntimeError("campaign count collapsed %d -> %d — refusing to overwrite"
                                   % (prev, len(rows)))
        except (KeyError, ValueError):
            log("WARN: previous data.json unreadable — skipping the collapse check")

    rows, kpis = decide_all(rows, THRESHOLDS)
    if kpis["spend_all"] <= 0:
        raise RuntimeError("total 30D spend is zero — refusing to overwrite")

    os.makedirs(FINAL, exist_ok=True)
    json.dump(dict(anchor=anchor, thresholds=THRESHOLDS, kpis=kpis, rows=rows),
              open(prev_path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    log("data.json written — %d campaigns, anchor %s" % (len(rows), anchor))

    for script in ("render_dashboard.py", "render_xlsx.py"):
        runpy.run_path(os.path.join(SQLDIR, script), run_name="__main__")

    # ---- publish: refresh the live ph_task row so the portal never lags the files -------------
    # Same task_id every week, so this REPLACES the row rather than adding one (no unique on
    # task_id -> delete+insert in one transaction, see eppa_publish_ph_task.publish).
    published = None
    if os.environ.get("PGPASSWORD"):
        sys.path.insert(0, HERE)
        from eppa_publish_ph_task import publish          # noqa: E402
        row_id, version, md5 = publish(quiet=True)
        published = dict(ph_task_id=row_id, version_level=version, html_md5=md5)
        log("published to ph_task id=%d version=%d md5=%s" % (row_id, version, md5))
    else:
        log("WARN: PGPASSWORD not set — files rebuilt but ph_task NOT refreshed")

    log("REFRESH OK — %d campaigns | %d pause (%d stock / %d rule1 / %d rule2) | £%.2f at risk"
        % (kpis["scope"], kpis["paused"], kpis["stock"], kpis["r1"], kpis["r2"],
           kpis["spend_at_risk"]))
    st = dict(anchor=anchor, campaigns=kpis["scope"], paused=kpis["paused"],
              stock=kpis["stock"], rule1=kpis["r1"], rule2=kpis["r2"],
              spend_at_risk=round(kpis["spend_at_risk"], 2))
    if published:
        st.update(published)
    write_status(True, "refresh ok", st)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        log("FAILED — %s" % exc)
        log(traceback.format_exc())
        write_status(False, str(exc))
        sys.exit(1)
