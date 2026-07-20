# -*- coding: utf-8 -*-
"""
EBPD — eBay Account Performance Dashboard · AUTONOMOUS weekly run (REQ-13-D02).
Runs headless (no MCP, no human): dynamic window -> pulls via psycopg2 -> builds HTML -> publishes to ph_task.

Reporting month = the LAST COMPLETE calendar month relative to run date (matches the live dashboard's logic).
LM = month before it; LY = same month last year.

Connections (env vars; passwords NEVER hardcoded — normally the global credential store,
see 05_documentation/capability/shared_db_credentials/):
  Warehouse (reads + ph_task write):  PGHOST PGPORT PGDATABASE PGUSER PGPASSWORD
  Ledsone (reads: New Listings):      LED_PGHOST LED_PGPORT LED_PGDATABASE LED_PGUSER LED_PGPASSWORD

FAILS CLOSED: every gate runs BEFORE any write. Any failure -> exit 2, nothing published.
Missing ledsone credentials are a HARD failure — New Listings must never silently publish as 0,
because a reader cannot tell a real zero from an absent connection.

Flags:  --no-publish / --dry-run  (build + validate only, write nothing)
Usage:  python ebpd_weekly_run.py [--dry-run]
Requires: build_html_v3.py alongside this file (its HTML template is reused verbatim).
"""
import os, re, sys, json, calendar, hashlib, datetime as _dt
from datetime import date, timedelta
import psycopg2
from psycopg2.extras import execute_values

HERE = os.path.dirname(os.path.abspath(__file__))
PUBLISH = not ("--no-publish" in sys.argv or "--dry-run" in sys.argv)
MIN_ROWS = int(os.getenv("EBPD_MIN_ROWS", "10"))   # catastrophic-failure floor (expect ~22)

def _status(state, msg):
    try:
        with open(os.path.join(HERE, "ebpd_status.txt"), "a", encoding="utf-8") as f:
            f.write("[%s]  %s  |  %s\n" % (_dt.datetime.now().strftime("%Y-%m-%d %H:%M"), state, msg))
    except Exception:
        pass

def die(m):
    print("[EBPD] ABORT: %s  -> nothing published" % m, flush=True)
    _status("FAILED", m)
    sys.exit(2)

# ---- connections (env, with the known warehouse defaults; ledsone must be provided) ----
WH = dict(host=os.getenv("PGHOST","149.28.134.54"), port=os.getenv("PGPORT","5435"),
          dbname=os.getenv("PGDATABASE","order_management_copy"),
          user=os.getenv("PGUSER","temp_user"), password=os.getenv("PGPASSWORD"))  # password via env (ebpd_secrets.bat)
LED = dict(host=os.getenv("LED_PGHOST"), port=os.getenv("LED_PGPORT","5432"),
           dbname=os.getenv("LED_PGDATABASE"), user=os.getenv("LED_PGUSER"),
           password=os.getenv("LED_PGPASSWORD"))
# ---- credential gates (fail closed, before any connection) ----
if not WH["password"]:
    die("warehouse PGPASSWORD not set - see 05_documentation/capability/shared_db_credentials/")
if not all([LED["host"], LED["dbname"], LED["user"], LED["password"]]):
    die("ledsone LED_PG* credentials not set - refusing to publish New Listings as a silent 0")
LED_OK = True

# ---- reporting window (dynamic) ----
def mbounds(y,m):
    s=date(y,m,1); e=date(y+(m==12), 1 if m==12 else m+1, 1); return s,e
today=date.today()
_lm_last=today.replace(day=1)-timedelta(days=1)         # last day of the last complete month
RY,RM=_lm_last.year,_lm_last.month                       # reporting month
js,je=mbounds(RY,RM)                                     # June-equivalent
ms_,me_=mbounds(RY-(RM==1),12 if RM==1 else RM-1)        # last month
ls,le=mbounds(RY-1,RM)                                   # last year same month
REP_LABEL=f"{calendar.month_name[RM]} {RY}"
NDAYS=calendar.monthrange(RY,RM)[1]                       # days in the reporting month (for date-range presets)
daily={}                                                  # (store,mkt) -> per-day arrays (idx0 = day 1)
def _dd(ss,mk):
    k=(ss,mk)
    if k not in daily:
        daily[k]={key:[0]*NDAYS for key in ("rev","ord","units","sp","sa","aod","ack","conv","click","newl")}
    return daily[k]
def d(x): return x.strftime("%Y-%m-%d")
print(f"[EBPD] reporting month = {REP_LABEL} ({d(js)}..{d(je)}) · LM {d(ms_)} · LY {d(ls)} · publish={PUBLISH} · ledsone={LED_OK}")

# display names for known stores; others derived
NAME_MAP={"led_sone":"LEDSONE UK","so_926407":"SUNSONE UK","electricalsone":"Electricalsone UK",
 "ledsonede":"LEDSONE DE","huettenlampen":"Huettenlampen DE","coventrylights":"Coventry Lights UK",
 "vintageinterior":"Vintage Interior UK","dctransformer":"DC Transformer UK","re6865":"RE6865 UK",
 "neighbourmarket":"Neighbour Market US","lighting_sone":"Lighting Sone UK","homin_gmbh":"Homin GmbH DE"}
def disp(store): return NAME_MAP.get(store, store.replace("_"," ").title())
MLAB={"UK":"UK","Germany":"DE","France":"FR","Italy":"IT","Ireland":"IE","US":"US","Canada":"CA"}
MKTS=["UK","Germany","France","Italy","Ireland","US","Canada"]

wh=psycopg2.connect(**WH); cur=wh.cursor()
def q(sql,args=None):
    cur.execute(sql,args or ()); return cur.fetchall()

# 1) active account list = eBay stores with Completed sales in the reporting month
accts=[r[0] for r in q("""SELECT ss_name FROM order_transaction
  WHERE source_name='EBAY' AND order_status='Completed' AND order_date>=%s AND order_date<%s
    AND market_place IS NOT NULL GROUP BY ss_name""",(d(js),d(je)))]
print(f"[EBPD] active eBay accounts this month: {len(accts)}")

# 2) sales by account x marketplace x period (order_total)
sales={}   # (store,mkt) -> {jun:[rev,ord,units], may:..., ly:...}
for label,(s,e) in {"jun":(js,je),"may":(ms_,me_),"ly":(ls,le)}.items():
    for ss,mk,od,un,rv in q("""SELECT ss_name,market_place,COUNT(DISTINCT order_id),SUM(quantity),
        ROUND(SUM(order_total)::numeric,2) FROM order_transaction
        WHERE source_name='EBAY' AND order_status='Completed' AND market_place IS NOT NULL
          AND ss_name = ANY(%s) AND order_date>=%s AND order_date<%s
        GROUP BY ss_name,market_place""",(accts,d(s),d(e))):
        sales.setdefault((ss,mk),{}).setdefault(label,[float(rv or 0),int(od or 0),int(un or 0)])

# 3) ON_SITE advertising by account x marketplace (reporting month) — spend + attributed sales/orders/clicks
adv={}
for ss,mk,sp,sa,ao,ck in q("""SELECT pp.ss_name,pp.marketplace,ROUND(SUM(pp.spend)::numeric,2),
      ROUND(SUM(pp.sales)::numeric,2),SUM(pp.orders),SUM(pp.clicks)
    FROM ppc_performance pp WHERE pp.source_name='EBAY' AND pp.record_type='campaign'
      AND pp.ss_name = ANY(%s) AND pp.date>=%s AND pp.date<%s
      AND pp.record_id IN (SELECT DISTINCT parent_id FROM ppc
          WHERE source_name ILIKE '%%ebay%%' AND record_main_type='campaign' AND record_subtype='ON_SITE')
    GROUP BY pp.ss_name,pp.marketplace HAVING SUM(pp.spend)>0""",(accts,d(js),d(je))):
    adv[(ss,mk)]=[float(sp),float(sa),int(ao or 0),int(ck or 0)]

# 4) whole-account conversion by account x marketplace x period (traffic_data which_channel=2)
conv={}
for label,(s,e) in {"jun":(js,je),"may":(ms_,me_),"ly":(ls,le)}.items():
    for ss,mk,cr in q("""SELECT sub_source_name,market_place,
        ROUND((SUM(conversion)/NULLIF(SUM(click),0))::numeric,4) FROM traffic_data
        WHERE which_channel=2 AND market_place IS NOT NULL AND sub_source_name = ANY(%s)
          AND date>=%s AND date<%s GROUP BY sub_source_name,market_place HAVING SUM(click)>0""",(accts,d(s),d(e))):
        conv.setdefault((ss,mk),{})[label]=float(cr) if cr is not None else None

# 5) active listings + stock by account x marketplace (current snapshot)
liststock={}
for ss,mk,ac,stk in q("""WITH la AS (SELECT sub_source_name a,market_place m,COUNT(DISTINCT ref_id) active
      FROM listing_data WHERE which_channel_name='ebay' AND sub_source_name = ANY(%s) AND market_place IS NOT NULL
      GROUP BY sub_source_name,market_place),
    sk AS (SELECT DISTINCT sub_source_name a,market_place m,COALESCE(NULLIF(mapped_sku,''),sku) sku
      FROM listing_data WHERE which_channel_name='ebay' AND sub_source_name = ANY(%s) AND market_place IS NOT NULL AND COALESCE(wrong_sku,0)=0),
    st AS (SELECT sk.a,sk.m,SUM(i.stock) stock FROM sk JOIN inv_final_stock i ON i.sku=sk.sku GROUP BY sk.a,sk.m)
    SELECT la.a,la.m,la.active,COALESCE(st.stock,0) FROM la LEFT JOIN st ON st.a=la.a AND st.m=la.m
    WHERE la.m = ANY(%s)""",(accts,accts,MKTS)):
    liststock[(ss,mk)]=[int(ac or 0),int(stk or 0)]

# 6) New Listings (ledsone DB, reporting month) — degrade to {} if ledsone creds absent
newl={}
if LED_OK:
    led=psycopg2.connect(**LED); lc=led.cursor()
    lc.execute("""SELECT ss.name, el.site, COUNT(DISTINCT el.item_id)
      FROM listings.ebay_listings el JOIN order_management.sub_source ss ON ss.id=el.sub_source
      WHERE el.created_at>=%s AND el.created_at<%s AND ss.name = ANY(%s)
      GROUP BY ss.name, el.site""",(d(js),d(je),accts))
    for ss,site,n in lc.fetchall(): newl[(ss,site)]=int(n)
    # New Listings DAILY (for date-range presets)
    lc.execute("""SELECT ss.name, el.site, el.created_at::date, COUNT(DISTINCT el.item_id)
      FROM listings.ebay_listings el JOIN order_management.sub_source ss ON ss.id=el.sub_source
      WHERE el.created_at>=%s AND el.created_at<%s AND ss.name = ANY(%s)
      GROUP BY ss.name, el.site, el.created_at::date""",(d(js),d(je),accts))
    for ss,site,dt,n in lc.fetchall():
        i=dt.day-1
        if 0<=i<NDAYS: _dd(ss,site)["newl"][i]=int(n)
    led.close(); print(f"[EBPD] New Listings pulled from ledsone: {sum(newl.values())} total")

# 7) DAILY warehouse pulls (sales / ON_SITE ads / conversion) for the date-range presets
for ss,mk,dt,od,un,rv in q("""SELECT ss_name,market_place,order_date::date,COUNT(DISTINCT order_id),SUM(quantity),SUM(order_total)
    FROM order_transaction WHERE source_name='EBAY' AND order_status='Completed' AND market_place IS NOT NULL
      AND ss_name = ANY(%s) AND order_date>=%s AND order_date<%s
    GROUP BY ss_name,market_place,order_date::date""",(accts,d(js),d(je))):
    i=dt.day-1
    if 0<=i<NDAYS:
        x=_dd(ss,mk); x["ord"][i]=int(od or 0); x["units"][i]=int(un or 0); x["rev"][i]=float(rv or 0)
for ss,mk,dt,sp,sa,ao,ck in q("""SELECT pp.ss_name,pp.marketplace,pp.date::date,SUM(pp.spend),SUM(pp.sales),SUM(pp.orders),SUM(pp.clicks)
    FROM ppc_performance pp WHERE pp.source_name='EBAY' AND pp.record_type='campaign' AND pp.ss_name = ANY(%s)
      AND pp.date>=%s AND pp.date<%s
      AND pp.record_id IN (SELECT DISTINCT parent_id FROM ppc WHERE source_name ILIKE '%%ebay%%' AND record_main_type='campaign' AND record_subtype='ON_SITE')
    GROUP BY pp.ss_name,pp.marketplace,pp.date::date""",(accts,d(js),d(je))):
    i=dt.day-1
    if 0<=i<NDAYS:
        x=_dd(ss,mk); x["sp"][i]=float(sp or 0); x["sa"][i]=float(sa or 0); x["aod"][i]=int(ao or 0); x["ack"][i]=int(ck or 0)
for ss,mk,dt,cv,ck in q("""SELECT sub_source_name,market_place,date::date,SUM(conversion),SUM(click)
    FROM traffic_data WHERE which_channel=2 AND market_place IS NOT NULL AND sub_source_name = ANY(%s)
      AND date>=%s AND date<%s GROUP BY sub_source_name,market_place,date::date""",(accts,d(js),d(je))):
    i=dt.day-1
    if 0<=i<NDAYS:
        x=_dd(ss,mk); x["conv"][i]=float(cv or 0); x["click"][i]=float(ck or 0)
print(f"[EBPD] daily buckets built for {len(daily)} account-marketplace pairs over {NDAYS} days")

# ---- assemble ROWS (same 12-field shape as build_html_v3.py R) ----
def g3(dic,key,label):
    v=dic.get(key,{}).get(label); return v
ROWS=[]
home_of={}  # store -> dominant marketplace of the reporting month (for the display suffix, informational)
for (ss,mk),per in sales.items():
    home_of.setdefault(ss, mk)
jun_active=[k for k in sales.keys() if sales[k].get("jun")]  # only account×marketplace with sales in the reporting month
for (ss,mk) in sorted(jun_active, key=lambda k:-(sales[k]["jun"][0])):
    per=sales[(ss,mk)]
    rev=[ (per.get("jun") or [None,None,None])[0], (per.get("may") or [None])[0] if per.get("may") else None, (per.get("ly") or [None])[0] if per.get("ly") else None ]
    od =[ (per.get("jun") or [None,None,None])[1], (per.get("may") or [None,None])[1] if per.get("may") else None, (per.get("ly") or [None,None])[1] if per.get("ly") else None ]
    un =[ (per.get("jun") or [None,None,None])[2], (per.get("may") or [None,None,None])[2] if per.get("may") else None, (per.get("ly") or [None,None,None])[2] if per.get("ly") else None ]
    cv=conv.get((ss,mk),{}); cvA=[cv.get("jun"),cv.get("may"),cv.get("ly")]
    ad=adv.get((ss,mk))
    ls_=liststock.get((ss,mk),[0,0])
    nl=newl.get((ss,mk),0)
    ROWS.append([disp(ss),ss,mk,MLAB.get(mk,mk),rev,od,un,cvA,ad,ls_[0],nl,ls_[1]])
print(f"[EBPD] assembled {len(ROWS)} account×marketplace rows · reporting revenue={round(sum(r[4][0] or 0 for r in ROWS),2)}")

# ---- VALIDATION GATES (fail closed, BEFORE any write) ----------------------
if not ROWS:                     die("0 account×marketplace rows - refusing to publish an empty dashboard")
if len(ROWS) < MIN_ROWS:         die(f"only {len(ROWS)} rows (< floor {MIN_ROWS}) - looks like a broken pull")

grain = [k for k in set((r[1], r[2]) for r in ROWS) if [ (x[1],x[2]) for x in ROWS ].count(k) > 1]
if grain:                        die(f"grain broken - {len(grain)} duplicated account×marketplace pair(s): {grain[:5]}")
if any((r[4][0] or 0) < 0 for r in ROWS):
    die("a row has negative reporting-month revenue")

# control total: the assembled rows must reconcile to a direct DB aggregate over the same window
rep_rev = round(sum(r[4][0] or 0 for r in ROWS), 2)
rep_ord = sum(r[5][0] or 0 for r in ROWS)
db_rev, db_ord = q("""SELECT ROUND(SUM(order_total)::numeric,2), COUNT(DISTINCT order_id)
    FROM order_transaction WHERE source_name='EBAY' AND order_status='Completed'
      AND market_place IS NOT NULL AND ss_name = ANY(%s) AND order_date>=%s AND order_date<%s""",
    (accts, d(js), d(je)))[0]
if abs(float(db_rev or 0) - rep_rev) > 0.01:
    die(f"control totals disagree: report revenue {rep_rev} vs DB {db_rev}")
print(f"[EBPD] control totals reconcile: revenue {rep_rev} | rows {rep_ord} orders vs DB {db_ord} distinct")

# Anchor DRIFT checks — the owner's own live-DB figures for the reference month (project CLAUDE.md).
# A closed month legitimately restates as refunds/cancellations land (verified 2026-07-20: led_sone UK
# moved 28,975.37 -> 28,941.61, i.e. -33.76 / -0.12%, matching 45 Refunded + 7 Cancelled June orders).
# So this is a DRIFT band, not an equality gate: it still catches a broken pull (orders of magnitude),
# while tolerating normal restatement. The drift is logged every run so erosion is never silent.
# ⚠ ANCHOR_TOL is a PROVISIONAL developer default — route to the Business Validator (Thinesh) to confirm.
ANCHOR_TOL = float(os.getenv("EBPD_ANCHOR_TOL", "0.01"))    # 1% of the signed-off value
if REP_LABEL == "June 2026":
    anchors = {("led_sone","UK"): ("revenue", 28975.37), ("so_926407","UK"): ("ad_spend", 884.07)}
    for (ss, mk), (what, want) in anchors.items():
        row = next((r for r in ROWS if r[1] == ss and r[2] == mk), None)
        if row is None:              die(f"anchor row {ss}/{mk} missing from the June 2026 rebuild")
        got = row[4][0] if what == "revenue" else ((row[8] or [None])[0])
        if got is None:              die(f"anchor {ss}/{mk} {what} is missing from the rebuild")
        drift = float(got) - want
        if abs(drift) > want * ANCHOR_TOL:
            die(f"anchor drift too large: {ss}/{mk} {what} = {got} vs signed-off {want} "
                f"({drift:+.2f}, {drift/want:+.2%} > {ANCHOR_TOL:.0%}) - investigate before publishing")
        print(f"[EBPD] anchor {ss}/{mk} {what}: {got} vs signed-off {want} ({drift:+.2f}, {drift/want:+.2%})")
print("[EBPD] validation: all gates PASSED")
wh.close()

# ---- build HTML via build_html_v3.build() — data pre-rendered as STATIC HTML (works with no JS) ----
sys.path.insert(0, HERE)
import build_html_v3
html=build_html_v3.build(ROWS, REP_LABEL, daily=daily, ndays=NDAYS)   # daily -> in-month date-range presets
if "__PAYLOAD__" in html:  die("dashboard template did not render (placeholder left)")
if len(html) < 100_000:    die(f"dashboard only {len(html)} bytes - render looks broken")
HTML_MD5 = hashlib.md5(html.encode("utf-8")).hexdigest()
OUT_HTML=os.path.join(HERE,"ebpd_auto_dashboard.html")
open(OUT_HTML,"w",encoding="utf-8").write(html)
print(f"[EBPD] HTML written: {OUT_HTML} ({len(html)} bytes)")

# ---- publish to ph_task (4 users) ----
ASSIGNED=["Thinesh","Jarsini","kobiga","powsteena"]
if PUBLISH:
    mtag=f"{RY}-{RM:02d}"                                  # reporting-month key: refresh within month, new row per month
    task_ids=[f"ebpd_{u}_ebay_account_performance_{mtag}" for u in ASSIGNED]
    legacy_ids=[f"ebpd_{u}_ebay_account_performance-V1" for u in ASSIGNED]   # one-time cleanup of the old fixed-id rows
    rows=[("eBay Account Performance Dashboard — monthly account KPIs across all eBay marketplaces — LEDsONE analytics platform",
           "ebpd", f"REQ-13-D01 eBay Account Performance Dashboard — {REP_LABEL} (auto weekly)",
           f"ebpd_{u}_ebay_account_performance_{mtag}","Development","Abiraj",u,"ebay_priors",html,
           f"eBay Account Performance Dashboard ({REP_LABEL}) — auto weekly refresh, all eBay accounts × marketplaces, order_total sales, ON_SITE ad + TACOS.",
           1,1,"released") for u in ASSIGNED]
    try:
        with psycopg2.connect(**WH) as conn:      # one transaction; auto-rollback on exception
            with conn.cursor() as pc:
                # delete this month's rows (refresh) + any leftover legacy fixed-id rows (dedupe the month)
                pc.execute("DELETE FROM tech_team_outputs.ph_task WHERE task_id = ANY(%s)",(task_ids+legacy_ids,))
                execute_values(pc,"""INSERT INTO tech_team_outputs.ph_task
                  (project_name,project_code,task_name,task_id,team,developer,assigned_user,assigned_user_team,
                   html_content,description,phase_level,version_level,version_status,created_at,updated_at)
                  VALUES %s RETURNING id,assigned_user""",rows,
                  template="(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),now())")
                pub=pc.fetchall()
                if len(pub)!=len(ASSIGNED):
                    raise RuntimeError(f"inserted {len(pub)} rows, expected {len(ASSIGNED)} - rolling back")
                # md5-verify every stored payload BEFORE the commit
                bad=[]
                for rid,user in pub:
                    pc.execute("SELECT md5(html_content) FROM tech_team_outputs.ph_task WHERE id=%s",(rid,))
                    if pc.fetchone()[0]!=HTML_MD5: bad.append((rid,user))
                if bad:
                    raise RuntimeError(f"md5 verify failed pre-commit {bad} - rolling back")
                for rid,user in pub: print(f"  published id={rid} user={user} md5={HTML_MD5[:8]}")
    except Exception as e:
        die(f"publish failed, transaction rolled back: {e}")
    print(f"[EBPD] published to ph_task ({len(ASSIGNED)} users), {len(ASSIGNED)} payloads md5-verified.")
else:
    print("[EBPD] --no-publish: skipped ph_task write.")
print("[EBPD] done.")

# ---- write a plain-English status line so a human can tell at a glance it ran & succeeded ----
try:
    import datetime as _dt
    stamp=_dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    act=("PUBLISHED to %d users"%len(ASSIGNED)) if PUBLISH else "built only (no publish)"
    rev=round(sum((r[4][0] or 0) for r in ROWS),2)
    line=f"[{stamp}]  OK  |  {REP_LABEL}  |  {len(ROWS)} rows  |  GBP {rev:,.2f}  |  New Listings {sum(newl.values())}  |  {act}\n"
    with open(os.path.join(HERE,"ebpd_status.txt"),"a",encoding="utf-8") as f:
        f.write(line)
    print("[EBPD] status recorded -> ebpd_status.txt")
except Exception as _e:
    print("[EBPD] (status line not written:", _e, ")")
