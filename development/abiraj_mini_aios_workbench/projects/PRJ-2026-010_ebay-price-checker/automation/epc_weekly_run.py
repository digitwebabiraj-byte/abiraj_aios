# -*- coding: utf-8 -*-
"""
EPC - eBay Price Checker - AUTONOMOUS weekly run (REQ-12, automation of D01).
Headless (no MCP, no human): pull live prices -> validate -> rebuild dashboard -> publish to ph_task.

Two databases (passwords NEVER hardcoded - supplied by epc_secrets.bat):
  ledsone   (READ  - the price data): LED_PGHOST LED_PGPORT LED_PGDATABASE LED_PGUSER LED_PGPASSWORD
  warehouse (WRITE - ph_task only)  : PGHOST PGPORT PGDATABASE PGUSER PGPASSWORD

Rule (owner CONFIRMED BUSINESS RULE 2026-07-16 + Thinesh Q1-Q8):
  target = Amazon (amazon Ledsone, sub_source 8, LOWEST) x0.90
         else website (Shopify ledsone/ledsone-de) x1.10
         else bundle = SUM(component price x pack qty) x0.90 / x1.10
         else DATA MISSING (NO COMPARATOR / BUNDLE)
  tolerance +/-0.50 below the 20 band, +/-1.00 at/above.  priority by money-at-risk.
  SKU-normalised per the AIOS KB: all_list=1, Amazon '_' suffix, ENC->sku_original, <char>PK pack qty.

FAILS CLOSED: every gate runs BEFORE any write. Any failure -> non-zero exit, nothing published.

Flags:  --no-publish / --dry-run   (build + validate only, write nothing)
Usage:  python epc_weekly_run.py [--dry-run]
Requires: epc_build_html.py alongside this file (the dashboard UI, single source of truth).
"""
import os, sys, time, datetime, hashlib
import psycopg2

HERE = os.path.dirname(os.path.abspath(__file__))
PUBLISH = not ("--no-publish" in sys.argv or "--dry-run" in sys.argv)
IMG_PREFIX = "https://i.ebayimg.com/"

# ---- business rules (owner-confirmed; edit here only) ----------------------
THRESHOLD, TOL_LO, TOL_HI = 20.0, 0.50, 1.00     # Q4/Q5
PRIO_HIGH, PRIO_MED       = 5.00, 2.00           # Q6 bands (developer defaults, owner-confirmed)
AMZ_SUB_SOURCE            = 8                    # Q3: 'amazon Ledsone'
WEB_SUB_UK, WEB_SUB_DE    = 104, 108             # Shopify ledsone / ledsone-de
ASSIGNED = ["Thinesh", "Jarsini", "kobiga", "powsteena"]
MIN_ROWS = int(os.getenv("EPC_MIN_ROWS", "50000"))   # catastrophic-failure floor (expect ~126k)

# (db_account, site) -> Thinesh's label.  Anything not here is NOT published.
LABEL = {
    ("led_sone","UK"):"LEDSone UK", ("electricalsone","UK"):"Electricalsone UK",
    ("so_926407","UK"):"Sunsone UK", ("vintageinterior","UK"):"Vintageinterior UK",
    ("coventrylights","UK"):"Coventrylight UK", ("lighting_sone","UK"):"Lightingsone UK",
    ("re6865","UK"):"Retro LED UK",
    ("huettenlampen","Germany"):"HUETTEN LAMP DE", ("ledsonede","Germany"):"Ledsone DE Reg DE",
    ("homin_gmbh","Germany"):"Homin DE", ("led_sone","Germany"):"LEDSone UK Reg DE",
    ("electricalsone","Germany"):"ElectricalSone DE", ("so_926407","Germany"):"Sunsone DE",
}

WH  = dict(host=os.getenv("PGHOST","149.28.134.54"), port=os.getenv("PGPORT","5435"),
           dbname=os.getenv("PGDATABASE","order_management_copy"),
           user=os.getenv("PGUSER","temp_user"), password=os.getenv("PGPASSWORD"))
LED = dict(host=os.getenv("LED_PGHOST"), port=os.getenv("LED_PGPORT","5432"),
           dbname=os.getenv("LED_PGDATABASE"), user=os.getenv("LED_PGUSER"),
           password=os.getenv("LED_PGPASSWORD"))

def log(m): print("[EPC] " + m, flush=True)
def die(m):
    log("ABORT: " + m + "  -> nothing published")
    _status("FAILED", m)
    sys.exit(2)

def _status(state, msg):
    try:
        with open(os.path.join(HERE, "epc_status.txt"), "a", encoding="utf-8") as f:
            f.write("[%s]  %s  |  %s\n" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), state, msg))
    except Exception:
        pass

def connect(cfg, what):
    """Connect with retry - the temp_user pool hits 'too many clients' intermittently."""
    last = None
    for attempt in range(1, 6):
        try:
            c = psycopg2.connect(connect_timeout=20, **cfg)
            c.set_client_encoding("UTF8")
            return c
        except Exception as e:
            last = e
            log("  %s connect attempt %d failed: %s" % (what, attempt, str(e).strip().splitlines()[0]))
            time.sleep(8)
    die("cannot connect to %s after 5 attempts: %s" % (what, last))

# ---- 1. PULL ---------------------------------------------------------------
SQL = """
WITH enc AS (SELECT sku, sku_original FROM inventory.products
             WHERE sku LIKE 'ENC%%' AND sku_original <> ''),
pk AS (SELECT pack_char, pack_qty FROM inventory.product_pk),
eb AS (
  SELECT e.item_id, e.sku AS raw_sku, e.price::numeric AS ebay_price, e.site,
         COALESCE(e.main_image_url,'') AS img, COALESCE(s.name,'') AS acct,
         COALESCE(en.sku_original, e.sku) AS nsku
  FROM listings.ebay_listings e
  LEFT JOIN order_management.sub_source s ON s.id = e.sub_source
  LEFT JOIN enc en ON en.sku = e.sku
  WHERE e.all_list = 1 AND e.site IN ('UK','Germany') AND e.price > 0 AND btrim(e.sku) <> ''
),
am AS (
  SELECT a.site, COALESCE(en.sku_original, split_part(a.sku,'_',1)) AS nsku,
         min(a.price)::numeric AS price
  FROM listings.amazon_listings a
  LEFT JOIN enc en ON en.sku = split_part(a.sku,'_',1)
  WHERE a.all_list = 1 AND a.sub_source = %(amz)s AND a.site IN ('UK','Germany') AND a.price > 0
  GROUP BY 1,2
),
wb AS (
  SELECT CASE WHEN w.sub_source = %(web_uk)s THEN 'UK' ELSE 'Germany' END AS site,
         COALESCE(en.sku_original, w.sku) AS nsku, min(w.price)::numeric AS price
  FROM listings.shopify_listings w
  LEFT JOIN enc en ON en.sku = w.sku
  WHERE w.all_list = 1 AND w.sub_source IN (%(web_uk)s, %(web_de)s) AND w.price > 0
  GROUP BY 1,2
),
combo AS (SELECT DISTINCT nsku, site FROM eb WHERE nsku LIKE '%%+%%'),
comp AS (
  SELECT c.nsku, c.site,
    CASE WHEN btrim(x.p) ~ '.[A-Za-z0-9]PK$' THEN substring(btrim(x.p),1,length(btrim(x.p))-3) ELSE btrim(x.p) END AS base,
    CASE WHEN btrim(x.p) ~ '.[A-Za-z0-9]PK$' THEN substring(btrim(x.p),length(btrim(x.p))-2,1) ELSE NULL END AS pchar
  FROM combo c, LATERAL unnest(string_to_array(c.nsku,'+')) AS x(p)
),
comp2 AS (SELECT c.*, COALESCE(pk.pack_qty,1) AS qty FROM comp c LEFT JOIN pk ON pk.pack_char = c.pchar),
bag AS (
  SELECT c.nsku, c.site, count(*) AS n_comp, count(am.price) AS n_amz, count(wb.price) AS n_web,
         sum(am.price*c.qty) AS sum_amz, sum(wb.price*c.qty) AS sum_web
  FROM comp2 c
  LEFT JOIN am ON am.nsku = c.base AND am.site = c.site
  LEFT JOIN wb ON wb.nsku = c.base AND wb.site = c.site
  GROUP BY 1,2
)
SELECT e.item_id, e.raw_sku, e.img, e.acct, e.site,
       COALESCE(w.price,  CASE WHEN b.n_web = b.n_comp THEN b.sum_web END) AS website_price,
       COALESCE(am.price, CASE WHEN b.n_amz = b.n_comp THEN b.sum_amz END) AS amazon_price,
       CASE WHEN am.price IS NOT NULL               THEN round(am.price*0.90, 2)
            WHEN w.price  IS NOT NULL               THEN round(w.price *1.10, 2)
            WHEN b.n_amz = b.n_comp AND b.sum_amz>0 THEN round(b.sum_amz*0.90, 2)
            WHEN b.n_web = b.n_comp AND b.sum_web>0 THEN round(b.sum_web*1.10, 2)
       END AS target_price,
       e.ebay_price
FROM eb e
LEFT JOIN am   ON am.nsku = e.nsku AND am.site = e.site
LEFT JOIN wb w ON w.nsku  = e.nsku AND w.site  = e.site
LEFT JOIN bag b ON b.nsku = e.nsku AND b.site  = e.site
"""

def main():
    log("start  publish=%s" % PUBLISH)
    if not all([LED["host"], LED["dbname"], LED["user"], LED["password"]]):
        die("ledsone credentials missing - copy epc_secrets.template.bat to epc_secrets.bat and fill LED_* in")
    if PUBLISH and not WH["password"]:
        die("warehouse PGPASSWORD missing (epc_secrets.bat)")

    led = connect(LED, "ledsone")
    try:
        with led.cursor() as c:
            c.execute(SQL, {"amz": AMZ_SUB_SOURCE, "web_uk": WEB_SUB_UK, "web_de": WEB_SUB_DE})
            raw = c.fetchall()
    finally:
        led.close()
    log("pulled %d live eBay UK+DE listing rows from ledsone" % len(raw))

    # ---- 2. APPLY RULES + FILTER TO THE 13 NAMED ACCOUNTS -------------------
    accounts = sorted(set(LABEL.values()))
    aidx = {a: i for i, a in enumerate(accounts)}
    rows, dropped, unknown = [], 0, set()
    kpi = {"normal": 0, "high": 0, "low": 0, "miss": 0, "missNoComp": 0, "missBundle": 0}
    for item_id, sku, img, acct, site, wp, ap, tgt, ebay in raw:
        label = LABEL.get((acct, site))
        if label is None:
            dropped += 1
            if acct: unknown.add((acct, site))
            continue
        wp   = float(wp)   if wp   is not None else None
        ap   = float(ap)   if ap   is not None else None
        tgt  = float(tgt)  if tgt  is not None else None
        ebay = float(ebay)
        if tgt is None:
            diff = pct = None; pc = 0
            sc = 4 if "+" in sku else 3
            kpi["miss"] += 1; kpi["missBundle" if sc == 4 else "missNoComp"] += 1
        else:
            diff = round(ebay - tgt, 2)
            pct  = round(diff / tgt, 4) if tgt else None
            tol  = TOL_LO if ebay < THRESHOLD else TOL_HI
            if abs(diff) <= tol: sc = 0; kpi["normal"] += 1
            elif diff > 0:       sc = 1; kpi["high"]   += 1
            else:                sc = 2; kpi["low"]    += 1
            m  = abs(diff)
            pc = 3 if m >= PRIO_HIGH else (2 if m >= PRIO_MED else 1)
        im = img[len(IMG_PREFIX):] if img.startswith(IMG_PREFIX) else (("!" + img) if img else "")
        rows.append([item_id, sku, im, aidx[label], wp, ap, tgt, ebay, diff, pct, sc, pc,
                     0 if site == "UK" else 1])
    total = len(rows)
    log("kept %d rows across the 13 named accounts (dropped %d from unnamed accounts)" % (total, dropped))
    log("  Normal %d | Too high %d | Too low %d | No target %d (no-comparator %d + bundle %d)"
        % (kpi["normal"], kpi["high"], kpi["low"], kpi["miss"], kpi["missNoComp"], kpi["missBundle"]))

    # ---- 3. VALIDATION GATES (fail closed, BEFORE any write) ---------------
    if total == 0:                       die("0 rows - refusing to publish an empty report")
    if total < MIN_ROWS:                 die("only %d rows (< floor %d) - looks like a broken pull" % (total, MIN_ROWS))
    if unknown:                          log("  note: unnamed accounts skipped: %s" % sorted(unknown)[:5])
    s = kpi["normal"] + kpi["high"] + kpi["low"] + kpi["miss"]
    if s != total:                       die("status counts %d != rows %d" % (s, total))
    if kpi["missNoComp"] + kpi["missBundle"] != kpi["miss"]:
        die("DATA MISSING split does not reconcile")
    if any(r[7] is None or r[7] <= 0 for r in rows):
        die("a row has a missing/non-positive eBay price")
    if any(r[3] is None for r in rows):  die("a row has no account index")
    log("validation: all gates PASSED")

    # ---- 4. BUILD THE DASHBOARD -------------------------------------------
    by_acc = {}
    stack  = {a: [0, 0, 0, 0] for a in accounts}
    for r in rows:
        a = accounts[r[3]]
        by_acc[a] = by_acc.get(a, 0) + 1
        stack[a][min(r[10], 3)] += 1
    acc_order = [a for a, _ in sorted(by_acc.items(), key=lambda kv: -kv[1])]
    payload = {"accounts": accounts, "accOrder": acc_order,
               "accStack": [[a] + stack[a] for a in acc_order],
               "kpi": dict(total=total, **kpi), "imgPrefix": IMG_PREFIX, "rows": rows}
    sys.path.insert(0, HERE)
    import epc_build_html
    html = epc_build_html.build(payload)
    if "__PAYLOAD__" in html:            die("dashboard template did not render (placeholder left)")
    if len(html) < 1_000_000:            die("dashboard only %d bytes - render looks broken" % len(html))
    html_md5 = hashlib.md5(html.encode("utf-8")).hexdigest()
    out = os.path.join(HERE, "epc_auto_dashboard.html")
    open(out, "w", encoding="utf-8").write(html)
    log("dashboard built: %s (%d bytes, md5 %s)" % (out, len(html), html_md5[:8]))

    # ---- 5. PUBLISH (guarded, one transaction, UPSERT the 4 users) ---------
    stamp = datetime.date.today().strftime("%Y-%m-%d")
    desc = ("eBay Price Checker (REQ-12-D01) - auto weekly refresh %s. Cross-channel price drift, %s live "
            "eBay UK & DE listings across 13 accounts. Target: Amazon x0.90, else website x1.10. "
            "Priced OK %s / Too high %s / Too low %s / No target %s. Status is item-price only - rank, don't reprice."
            % (stamp, f"{total:,}", f"{kpi['normal']:,}", f"{kpi['high']:,}", f"{kpi['low']:,}", f"{kpi['miss']:,}"))
    if not PUBLISH:
        log("--dry-run: validated and built, wrote nothing to ph_task.")
        _status("OK(dry-run)", "%s rows | built only" % f"{total:,}")
        log("done."); return

    wh = connect(WH, "warehouse")
    try:
        with wh:                                     # one transaction; auto-rollback on exception
            with wh.cursor() as pc:
                touched = []
                for u in ASSIGNED:
                    tid = "epc_%s_ebay_price_checker-V1" % u
                    pc.execute("""UPDATE tech_team_outputs.ph_task
                                     SET html_content=%s, description=%s,
                                         version_level=version_level+1, updated_at=now()
                                   WHERE task_id=%s AND project_code='epc'
                               RETURNING id, version_level""", (html, desc, tid))
                    got = pc.fetchone()
                    if got is None:                   # a user was added since the last run
                        pc.execute("""INSERT INTO tech_team_outputs.ph_task
                            (project_name,project_code,task_name,task_id,team,developer,assigned_user,
                             assigned_user_team,html_content,description,phase_level,version_level,version_status)
                            VALUES (%s,'epc',%s,%s,'Development','Abiraj',%s,'ebay_priors',%s,%s,1,1,'released')
                            RETURNING id, version_level""",
                            ("eBay Price Checker - Amazon-first cross-channel price drift (Amazon / Website / eBay), "
                             "UK & Germany, 13 eBay accounts - LEDsONE analytics platform",
                             "REQ-12-D01 eBay Price Checker - UK & DE price-drift report (auto weekly)",
                             tid, u, html, desc))
                        got = pc.fetchone()
                        log("  INSERTED new row for %s -> id %s" % (u, got[0]))
                    else:
                        log("  updated %-10s -> id %s (version %s)" % (u, got[0], got[1]))
                    touched.append(got[0])
                if len(touched) != len(ASSIGNED):
                    raise RuntimeError("expected %d rows, touched %d" % (len(ASSIGNED), len(touched)))

                # md5-verify every stored payload BEFORE the commit. A truncated or
                # re-encoded write is invisible to every check above - the transaction
                # succeeds and commits a corrupted dashboard. Read it back and compare.
                # NOTE: version_status is deliberately NOT asserted. A user marking their own
                # task 'completed' in ph_task is normal workflow, not corruption - kobiga's row
                # (id 300) was already 'completed' on 2026-07-21. Asserting 'released' here would
                # roll back every future publish because someone actioned their task. Only
                # assigned_user_team is a correctness property: wrong tag = a report nobody sees.
                bad, statuses = [], []
                for rid in touched:
                    pc.execute("SELECT md5(html_content), assigned_user_team, version_status "
                               "FROM tech_team_outputs.ph_task WHERE id=%s", (rid,))
                    stored_md5, team_tag, ver_status = pc.fetchone()
                    statuses.append(ver_status)
                    if stored_md5 != html_md5:
                        bad.append(("md5", rid))
                    elif team_tag != "ebay_priors":
                        bad.append(("routing team=%s" % team_tag, rid))
                if bad:
                    raise RuntimeError("pre-commit verify failed %s - rolling back" % bad)
                log("  verified %d payloads md5=%s, routing ebay_priors intact (statuses: %s)"
                    % (len(touched), html_md5[:8], ", ".join(sorted(set(statuses)))))
    except Exception as e:
        die("publish failed, transaction rolled back: %s" % str(e).strip().splitlines()[-1])
    finally:
        wh.close()
    log("published to ph_task for %d users: ids %s" % (len(ASSIGNED), touched))
    _status("OK", "%s rows | OK %s / high %s / low %s / none %s | published to %d users"
            % (f"{total:,}", f"{kpi['normal']:,}", f"{kpi['high']:,}", f"{kpi['low']:,}",
               f"{kpi['miss']:,}", len(ASSIGNED)))
    log("done.")

if __name__ == "__main__":
    main()
