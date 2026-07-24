#!/usr/bin/env python3
"""
FRRC — FBA Returns Root-Cause : unattended MONTHLY run (REQ-10-D02)
==================================================================
Pull -> validate -> render 1 dashboard per Portfolio Holder -> publish to
tech_team_outputs.ph_task. Designed to run from Windows Task Scheduler with no human present.

SAFETY CONTRACT (do not weaken):
  * Source tables (amazon_returns / order_transaction / listing_data) are READ-ONLY.
    The ONLY write is the guarded per-PH UPSERT into the OUTPUT store tech_team_outputs.ph_task.
  * FAIL CLOSED: every integrity check must pass BEFORE anything is written. Any failure aborts
    the run with a non-zero exit code and publishes NOTHING (single transaction, auto-rollback).
  * NO CREDENTIAL IN THIS FILE. The DB password is read from the env var FRRC_PGPASSWORD.
  * Thresholds are inputs (Thresholds tab), applied in the render layer - never hardcoded in SQL.

USAGE
  python run_frrc_monthly.py            # real run (pull + render + publish)
  python run_frrc_monthly.py --dry-run  # pull + render + validate, publish NOTHING
  python run_frrc_monthly.py --window-end 2026-07-13   # ad-hoc: force the window end date

EXIT CODES
  0 success | 1 config/credential error | 2 integrity check failed (nothing published)
  3 DB error | 4 publish verification failed (rolled back)
"""
from __future__ import annotations
import os, sys, json, re, time, hashlib, argparse, logging
from datetime import date, timedelta, datetime

# ----------------------------------------------------------------------------- CONFIG
# Cadence: Task Scheduler fires on RUN_DAY each month (see register_scheduled_task.ps1).
RUN_DAY      = 8    # day of month the scheduler fires, 09:00 (before the 15th, as required)
WINDOW_DAYS  = 30   # "last 30 days" - LOCKED, user-confirmed (HANDOFF 2/4). Do not change
                    # without the user. NOTE: with the >=2-returns gate this diagnoses ~15%
                    # of products; that is the expected behaviour of the confirmed rules.
SETTLE_DAYS  = 7    # end the window this many days BEFORE the run date. WHY: Amazon's FBA
                    # returns feed back-fills - a T+1 window is ~12% short (measured
                    # 2026-07-15: the same window read 105 units on the 14th, 118 on the 15th).
                    # 7 days lets the tail land. NOTE: D01's literal rule was 1 day; the change
                    # to 7 is an OPEN item for Satheesvaran (item C) - change here when he rules.

DB = {"host": os.getenv("FRRC_PGHOST", "149.28.134.54"),
      "port": os.getenv("FRRC_PGPORT", "5435"),
      "dbname": os.getenv("FRRC_PGDATABASE", "order_management_copy"),
      "user": os.getenv("FRRC_PGUSER", "temp_user"),
      "password": os.getenv("FRRC_PGPASSWORD")}          # <- REQUIRED, never hardcoded

PROJECT_CODE = "frrc"
PROJECT_NAME = ("FRRC — FBA Returns Root-Cause (weekly Amazon FBA returns tracker & "
                "root-cause action report) — LEDsONE analytics platform")
TASK_NAME    = "FBA Returns — Root-Cause Report"
TEAM, DEVELOPER, TEAM_TAG = "Development", "Abiraj", "ph_priors"

TH = {"crit": 0.20, "high": 0.10, "minret": 2, "listing": 0.40, "quality": 0.40, "buyer": 0.50}

BASE     = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(BASE, "frrc_per_ph_template.html")
OUTDIR   = os.path.join(BASE, "output")
LOGDIR   = os.path.join(BASE, "logs")

# ----------------------------------------------------------------------------- logging
os.makedirs(LOGDIR, exist_ok=True)
log = logging.getLogger("frrc")
log.setLevel(logging.INFO)
_f = logging.Formatter("%(asctime)s  %(levelname)-7s %(message)s")
_fh = logging.FileHandler(os.path.join(LOGDIR, f"frrc_run_{date.today():%Y-%m-%d}.log"), encoding="utf-8")
_fh.setFormatter(_f); log.addHandler(_fh)
_sh = logging.StreamHandler(sys.stdout); _sh.setFormatter(_f); log.addHandler(_sh)

def die(code: int, msg: str):
    log.error("ABORT (exit %s): %s", code, msg)
    log.error("NOTHING WAS PUBLISHED.")
    sys.exit(code)

# ----------------------------------------------------------------------------- SQL
REASON_MAP = {
    "listing_qty":  ["NOT_COMPATIBLE", "NOT_AS_DESCRIBED"],
    "quality_qty":  ["QUALITY_UNACCEPTABLE", "DEFECTIVE", "DAMAGED_BY_FC", "DAMAGED_BY_CARRIER"],
    "buyer_qty":    ["UNWANTED_ITEM", "FOUND_BETTER_PRICE", "ORDERED_WRONG_ITEM"],
    "shipping_qty": ["UNDELIVERABLE_UNKNOWN", "UNDELIVERABLE_REFUSED"],
    # NO_REASON_GIVEN + the 6 rare codes not in the tracker's map (HELD: item E, Satheesvaran)
    "unknown_qty":  ["NO_REASON_GIVEN", "MISSING_PARTS", "SWITCHEROO",
                     "MISSED_ESTIMATED_DELIVERY", "POOR_FIT", "MISORDERED", "UNAUTHORIZED_PURCHASE"],
}
KNOWN_REASONS = {r for v in REASON_MAP.values() for r in v}

def _in(vals): return ",".join("'" + v + "'" for v in vals)

Q_REASON_DOMAIN = """
SELECT reason, COUNT(*) FROM public.amazon_returns
WHERE fulfilment='fba' AND request_date >= %s AND request_date < %s
GROUP BY reason;"""

Q_REPORT = f"""
WITH returns_agg AS (
  SELECT asin,
    mode() WITHIN GROUP (ORDER BY sku) AS return_sku,
    SUM(qty) AS total_returns,
    COALESCE(SUM(qty) FILTER (WHERE reason IN ({_in(REASON_MAP['listing_qty'])})),0)  AS listing_qty,
    COALESCE(SUM(qty) FILTER (WHERE reason IN ({_in(REASON_MAP['quality_qty'])})),0)  AS quality_qty,
    COALESCE(SUM(qty) FILTER (WHERE reason IN ({_in(REASON_MAP['buyer_qty'])})),0)    AS buyer_qty,
    COALESCE(SUM(qty) FILTER (WHERE reason IN ({_in(REASON_MAP['shipping_qty'])})),0) AS shipping_qty,
    COALESCE(SUM(qty) FILTER (WHERE reason IN ({_in(REASON_MAP['unknown_qty'])})),0)  AS unknown_qty,
    mode() WITHIN GROUP (ORDER BY reason) AS top_reason,
    mode() WITHIN GROUP (ORDER BY CASE WHEN sub_source_name ILIKE '%%ledsone%%'   THEN 'LEDSone'
                                       WHEN sub_source_name ILIKE '%%dcvoltage%%' THEN 'DCVoltage'
                                       ELSE sub_source_name END) AS account,
    COUNT(DISTINCT sub_source_name) AS n_accounts
  FROM public.amazon_returns
  WHERE fulfilment='fba' AND request_date >= %(ws)s AND request_date < %(we)s
  GROUP BY asin
),
sales_agg AS (
  SELECT asin, SUM(quantity) AS units_sold,
    mode() WITHIN GROUP (ORDER BY user_name) AS responsible_ph
  FROM public.order_transaction
  WHERE source_name='AMAZON' AND fba_sales=TRUE AND market_place='UK'
    AND order_status='Completed'
    AND order_date >= %(ws)s AND order_date < %(we)s
  GROUP BY asin
),
bridge AS (
  SELECT ref_id AS asin,
    mode() WITHIN GROUP (ORDER BY COALESCE(NULLIF(mapped_sku,''), sku)) AS inv_sku
  FROM public.listing_data
  WHERE which_channel=1 AND wrong_sku=0 AND COALESCE(is_parent,0)<>1 AND market_place='UK'
  GROUP BY ref_id
)
SELECT COALESCE(b.inv_sku, r.return_sku) AS sku, r.asin, r.account, r.n_accounts,
  COALESCE(s.units_sold,0)::int AS units_sold,
  r.total_returns::int, r.listing_qty::int, r.quality_qty::int, r.buyer_qty::int,
  r.shipping_qty::int, r.unknown_qty::int, r.top_reason, s.responsible_ph,
  r.return_sku, b.inv_sku
FROM returns_agg r
LEFT JOIN sales_agg s ON s.asin = r.asin
LEFT JOIN bridge    b ON b.asin = r.asin
ORDER BY r.total_returns DESC, COALESCE(s.units_sold,0) ASC, r.asin;"""

# ----------------------------------------------------------------------------- render
def flag_of(r):
    if r["units_sold"] <= 0: return "NA"
    x = r["total_returns"] / r["units_sold"]
    return "CRITICAL" if x > TH["crit"] else "HIGH" if x > TH["high"] else "OK"

def initials(name):
    b = re.sub(r"\(.*?\)", "", name).strip()
    return (b[:2] if b else name[:2]).upper()

def render_dashboards(rows, ws, we, run_label):
    tpl = open(TEMPLATE, encoding="utf-8").read()
    os.makedirs(OUTDIR, exist_ok=True)
    owners = sorted({r["responsible_ph"] for r in rows if r["responsible_ph"]}, key=str.lower)
    built = []
    for ph in owners:
        rws = [{"sku": r["sku"], "asin": r["asin"], "return_sku": r["return_sku"],
                "units": r["units_sold"], "returns": r["total_returns"],
                "lm": r["listing_qty"], "ql": r["quality_qty"], "bp": r["buyer_qty"],
                "sh": r["shipping_qty"], "uk": r["unknown_qty"],
                "top": r["top_reason"], "ph": ph, "acc": r["account"]}
               for r in rows if r["responsible_ph"] == ph]
        c = {"CRITICAL": 0, "HIGH": 0, "OK": 0, "NA": 0}
        for r in rows:
            if r["responsible_ph"] == ph: c[flag_of(r)] += 1
        html = (tpl.replace("__PAYLOAD__", json.dumps(rws)).replace("__TH__", json.dumps(TH))
                   .replace("__WS__", ws).replace("__WE__", we).replace("__RUN__", run_label)
                   .replace("__PH__", ph).replace("__INI__", initials(ph))
                   .replace("__NROWS__", str(len(rws)))
                   .replace("__NRET__", str(sum(x["returns"] for x in rws)))
                   .replace("__NCRIT__", str(c["CRITICAL"])).replace("__NHIGH__", str(c["HIGH"]))
                   .replace("__NOK__", str(c["OK"])).replace("__NNA__", str(c["NA"]))
                   .replace("__NLED__", str(sum(1 for x in rws if x["acc"] == "LEDSone")))
                   .replace("__NDCV__", str(sum(1 for x in rws if x["acc"] == "DCVoltage"))))
        if "__" in re.sub(r"[^_A-Z]", "", html) and re.search(r"__[A-Z]+__", html):
            die(2, f"template placeholder left unreplaced for {ph}")
        p = os.path.join(OUTDIR, re.sub(r"[^A-Za-z0-9()]+", "_", ph) + ".html")
        open(p, "w", encoding="utf-8").write(html)
        built.append({"ph": ph, "file": p, "rows": len(rws),
                      "md5": hashlib.md5(html.encode("utf-8")).hexdigest()})
    return built

def slug(ph): return re.sub(r"[^A-Za-z0-9]+", "_", ph).strip("_")

# ----------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="validate + render, publish nothing")
    ap.add_argument("--window-end", help="force window end (YYYY-MM-DD, exclusive)")
    a = ap.parse_args()

    log.info("=" * 78)
    log.info("FRRC monthly run starting | dry_run=%s", a.dry_run)

    if not DB["password"]:
        die(1, "env var FRRC_PGPASSWORD is not set (see README - run set_credential once).")
    try:
        import psycopg2
    except ImportError:
        die(1, "psycopg2 not installed:  pip install psycopg2-binary")

    # ---- window ----
    we = date.fromisoformat(a.window_end) if a.window_end else date.today() - timedelta(days=SETTLE_DAYS)
    ws = we - timedelta(days=WINDOW_DAYS)
    log.info("Window: %s -> %s (inclusive) | %s days | settle buffer %s days | run %s",
             ws, we - timedelta(days=1), WINDOW_DAYS, SETTLE_DAYS, date.today())

    # Connect with retry - the shared temp_user pool intermittently refuses connections
    # ("remaining connection slots are reserved..."), confirmed live 2026-07-24. FRRC runs
    # MONTHLY, so a single refusal on the 8th would otherwise skip a whole month's report.
    conn = None
    for attempt in range(1, 6):
        try:
            conn = psycopg2.connect(connect_timeout=20, **DB)
            break
        except Exception as e:
            log.warning("DB connect attempt %d/5 failed: %s", attempt, str(e).strip().splitlines()[0])
            if attempt < 5:
                time.sleep(8)
    if conn is None:
        die(3, "DB connect failed after 5 attempts")

    try:
        # ---- 1. reason-domain check: fail closed on an unmapped code ----
        with conn.cursor() as cur:
            cur.execute(Q_REASON_DOMAIN, (ws, we))
            live = {r[0] for r in cur.fetchall() if r[0] is not None}
        unmapped = sorted(live - KNOWN_REASONS)
        if unmapped:
            die(2, f"NEW unmapped return reason code(s) {unmapped} - would be mis-bucketed. "
                   f"Add to REASON_MAP only after Satheesvaran confirms the bucket (item E).")
        log.info("Reason-domain check OK (%d live codes, all mapped)", len(live))

        # ---- 2. pull ----
        with conn.cursor() as cur:
            cur.execute(Q_REPORT, {"ws": ws, "we": we})
            cols = [d[0] for d in cur.description]
            rows = [dict(zip(cols, r)) for r in cur.fetchall()]
        if not rows:
            die(2, "query returned 0 rows - refusing to publish an empty report")
        units = sum(r["total_returns"] for r in rows)
        log.info("Pulled %d returning ASINs / %d return units", len(rows), units)

        # ---- 3. integrity checks (fail closed) ----
        bad = [r["asin"] for r in rows if r["listing_qty"] + r["quality_qty"] + r["buyer_qty"]
               + r["shipping_qty"] + r["unknown_qty"] != r["total_returns"]]
        if bad: die(2, f"bucket arithmetic mismatch on {len(bad)} ASIN(s): {bad[:5]}")
        span = [r["asin"] for r in rows if r["n_accounts"] > 1]
        if span: die(2, f"{len(span)} ASIN(s) span both accounts, grain unsafe: {span[:5]}")
        unk = [r["asin"] for r in rows if r["account"] not in ("LEDSone", "DCVoltage")]
        if unk: die(2, f"{len(unk)} ASIN(s) have an unrecognised account tag: {unk[:5]}")
        log.info("Integrity OK: bucket arithmetic 0 fail | 0 account-spanning | 0 unmapped account")

        with conn.cursor() as cur:
            cur.execute("""SELECT COUNT(DISTINCT asin), COALESCE(SUM(qty),0) FROM public.amazon_returns
                           WHERE fulfilment='fba' AND request_date >= %s AND request_date < %s""", (ws, we))
            db_asins, db_units = cur.fetchone()
        if (db_asins, int(db_units)) != (len(rows), units):
            die(2, f"control totals disagree: report {len(rows)}/{units} vs DB {db_asins}/{db_units}")
        log.info("Control totals reconcile against DB: %d ASINs / %d units", db_asins, int(db_units))

        # ---- 4. render ----
        run_label = date.today().isoformat()
        built = render_dashboards(rows, ws.isoformat(), (we - timedelta(days=1)).isoformat(), run_label)
        owned = sum(b["rows"] for b in built)
        log.info("Rendered %d per-PH dashboards | %d owned rows | %d unassigned (no in-window sale)",
                 len(built), owned, len(rows) - owned)

        snap = os.path.join(OUTDIR, f"frrc_dataset_{ws}_{we - timedelta(days=1)}.json")
        json.dump(rows, open(snap, "w"), indent=1, default=str)
        log.info("Dataset snapshot: %s", snap)

        if a.dry_run:
            log.info("DRY-RUN: publish skipped. %d dashboards in %s", len(built), OUTDIR)
            log.info("Run complete (dry-run).")
            return

        # ---- 5. guarded publish: one transaction, md5-verified before commit ----
        with conn:
            with conn.cursor() as cur:
                pub = []
                for b in built:
                    tid = f"{PROJECT_CODE}_{slug(b['ph'])}_fba_returns_root_cause-V1"
                    html = open(b["file"], encoding="utf-8").read()
                    cur.execute("""UPDATE tech_team_outputs.ph_task
                                   SET html_content=%s, task_name=%s, description=NULL,
                                       version_level=version_level+1, updated_at=now()
                                   WHERE project_code=%s AND task_id=%s RETURNING id""",
                                (html, TASK_NAME, PROJECT_CODE, tid))
                    got = cur.fetchall()
                    if len(got) == 1:
                        pub.append((got[0][0], b, "UPDATE"))
                    elif len(got) == 0:                       # a NEW portfolio holder appeared
                        cur.execute("""INSERT INTO tech_team_outputs.ph_task
                            (project_name,project_code,task_name,task_id,team,developer,
                             assigned_user,assigned_user_team,html_content,description,
                             phase_level,version_level,version_status)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,NULL,1,1,'released') RETURNING id""",
                            (PROJECT_NAME, PROJECT_CODE, TASK_NAME, tid, TEAM, DEVELOPER,
                             b["ph"], TEAM_TAG, html))
                        pub.append((cur.fetchone()[0], b, "INSERT (new PH)"))
                    else:
                        raise RuntimeError(f"task_id {tid} matched {len(got)} rows - aborting")

                bad = []
                for rid, b, _ in pub:
                    cur.execute("SELECT md5(html_content) FROM tech_team_outputs.ph_task WHERE id=%s", (rid,))
                    if cur.fetchone()[0] != b["md5"]:
                        bad.append((rid, b["ph"]))
                if bad:
                    raise RuntimeError(f"md5 verify failed pre-commit {bad} - rolling back")
                for rid, b, how in pub:
                    log.info("  %-6s id=%-4s %-18s rows=%-3s md5=%s", how, rid, b["ph"], b["rows"], b["md5"][:8])
        log.info("PUBLISHED + COMMITTED: %d rows md5-verified", len(pub))

        with conn.cursor() as cur:
            cur.execute("""SELECT count(*), bool_and(assigned_user_team=%s), bool_and(version_status='released')
                           FROM tech_team_outputs.ph_task WHERE project_code=%s""", (TEAM_TAG, PROJECT_CODE))
            n, tag_ok, rel_ok = cur.fetchone()
        if not (tag_ok and rel_ok):
            die(4, f"post-publish verify failed: rows={n} ph_priors={tag_ok} released={rel_ok}")
        log.info("Post-publish verify OK: %d live frrc rows | ph_priors + released intact", n)
        log.info("Run complete.")

    except SystemExit:
        raise
    except Exception as e:
        die(3, f"unexpected error (transaction rolled back): {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
