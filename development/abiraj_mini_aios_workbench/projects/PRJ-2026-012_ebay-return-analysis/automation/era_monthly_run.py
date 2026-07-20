# -*- coding: utf-8 -*-
"""
ERA — eBay Return Analysis Dashboard · AUTONOMOUS monthly run (REQ-14-D02).
Runs headless (no MCP, no human) on the 5th of each month: dynamic window -> pulls the canonical
return-analysis query per in-month preset window from the live `ledsone` DB (read-only) -> builds the
light-theme HTML with the date-range dropdown -> publishes to tech_team_outputs.ph_task.

Governance identity (project_code ERA):
  project        = eBay Return Analysis
  project_code   = ERA
  phase          = Phase — Reporting & Presentation (eBay Return Analysis Dashboard — first governed report)
  requirement_id = REQ-14   ·   deliverable_id = REQ-14-D01

Reporting month = the LAST COMPLETE calendar month relative to run date (on the 5th of month N -> month N-1).

Connections (env vars; passwords NEVER hardcoded — normally the global credential store,
see 05_documentation/capability/shared_db_credentials/):
  Ledsone (READ, the data):        LED_PGHOST LED_PGPORT LED_PGDATABASE LED_PGUSER LED_PGPASSWORD
  Warehouse (WRITE, ph_task only): PGHOST PGPORT PGDATABASE PGUSER PGPASSWORD

FAILS CLOSED: every gate runs BEFORE any write. Any failure -> exit 2, nothing published.

Flags:  --no-publish / --dry-run   (build + validate only; do NOT write ph_task)
Usage:  python era_monthly_run.py [--dry-run] [YYYY-MM]
Requires: build_returns_live_html.py + build_returns_html.py + the mockup xlsx (in evidence/final_outputs).
"""
import os, sys, calendar, hashlib
from datetime import date, timedelta, datetime
import psycopg2
from psycopg2.extras import execute_values

HERE = os.path.dirname(os.path.abspath(__file__))
MIN_SKUS = int(os.getenv("ERA_MIN_SKUS", "20"))   # catastrophic-failure floor (June reference = 144)

def _status(state, msg):
    try:
        with open(os.path.join(HERE, "era_status.txt"), "a", encoding="utf-8") as f:
            f.write("[%s]  %s  |  %s\n" % (datetime.now().strftime("%Y-%m-%d %H:%M"), state, msg))
    except Exception:
        pass

def die(m):
    print("[ERA] ABORT: %s  -> nothing published" % m, flush=True)
    _status("FAILED", m)
    sys.exit(2)
PROJECT = os.path.dirname(HERE)
FINAL_DIR = os.path.join(PROJECT, "evidence", "final_outputs", "REQ-14_ebay-return-analysis")
MOCKUP = os.path.join(FINAL_DIR, "eBay_Return_Analysis_June2026.xlsx")
sys.path.insert(0, FINAL_DIR)
import build_returns_live_html as BL   # generate(), month_ctx()

PUBLISH = not ("--no-publish" in sys.argv or "--dry-run" in sys.argv)
MONTH_ARG = next((a for a in sys.argv[1:] if a[:2] == "20" and "-" in a), None)

# ---- governance identity ----
PROJECT_NAME = "eBay Return Analysis"
PROJECT_CODE = "ERA"
REQUIREMENT_ID = "REQ-14"
DELIVERABLE_ID = "REQ-14-D01"
PHASE = "Phase — Reporting & Presentation (eBay Return Analysis Dashboard — first governed report)"

# report recipients — the eBay team group (same as PRJ-2026-010 epc / PRJ-2026-011 ebpd)
ASSIGNED = ["Thinesh", "Jarsini", "kobiga", "powsteena"]
ASSIGNED_USER_TEAM = "ebay_priors"

# ---- ledsone (read) + warehouse (publish) connections from env ----
LED = dict(host=os.getenv("LED_PGHOST"), port=os.getenv("LED_PGPORT", "5432"),
           dbname=os.getenv("LED_PGDATABASE"), user=os.getenv("LED_PGUSER"),
           password=os.getenv("LED_PGPASSWORD"))
WH = dict(host=os.getenv("PGHOST", "149.28.134.54"), port=os.getenv("PGPORT", "5435"),
          dbname=os.getenv("PGDATABASE", "order_management_copy"),
          user=os.getenv("PGUSER", "temp_user"), password=os.getenv("PGPASSWORD"))

def reporting_month():
    if MONTH_ARG:
        return MONTH_ARG
    last_of_prev = date.today().replace(day=1) - timedelta(days=1)
    return "%04d-%02d" % (last_of_prev.year, last_of_prev.month)

def log(msg): print("[ERA] " + msg, flush=True)

def main():
    month = reporting_month()
    ctx = BL.month_ctx(month)
    log("reporting month = %s (%s) · publish=%s" % (month, ctx["label"], PUBLISH))

    if not all([LED["host"], LED["dbname"], LED["user"], LED["password"]]):
        die("ledsone LED_PG* credentials not set - see 05_documentation/capability/shared_db_credentials/")
    if PUBLISH and not WH["password"]:
        die("warehouse PGPASSWORD not set - cannot publish")

    led = psycopg2.connect(**LED); led.set_session(readonly=True, autocommit=True)
    html, views_data, cache, stats = BL.generate(month, led, MOCKUP)
    led.close()
    log("built %s: %d SKUs / %d returns / £%.2f refund / £%.2f ad spend / ACOS %.1f%% / ROAS %.2fx"
        % (stats["month"], stats["n"], stats["returns"], stats["refund"], stats["spend"],
           (stats["acos"] or 0) * 100, stats["roas"] or 0))

    # ---- VALIDATION GATES (fail closed, BEFORE any write) ------------------
    if not stats["n"]:              die("0 SKU rows - refusing to publish an empty dashboard")
    if stats["n"] < MIN_SKUS:       die("only %d SKU rows (< floor %d) - looks like a broken pull"
                                        % (stats["n"], MIN_SKUS))
    if stats["returns"] < stats["n"]:
        die("%d returns across %d SKUs - every listed SKU must have >= 1 return"
            % (stats["returns"], stats["n"]))
    for k in ("refund", "spend"):
        if stats[k] is not None and stats[k] < 0:  die("negative %s (%.2f) - arithmetic broken" % (k, stats[k]))
    # the June 2026 reference build is the signed-off anchor (project CLAUDE.md) - never drift from it
    if month == "2026-06" and (stats["n"], stats["returns"]) != (144, 153):
        die("June 2026 anchor failed: %d SKUs / %d returns, expected 144 / 153"
            % (stats["n"], stats["returns"]))
    if "__PAYLOAD__" in html:       die("dashboard template did not render (placeholder left)")
    if len(html) < 100_000:         die("dashboard only %d bytes - render looks broken" % len(html))
    html_md5 = hashlib.md5(html.encode("utf-8")).hexdigest()
    log("validation: all gates PASSED (md5 %s)" % html_md5[:8])

    out_html = os.path.join(HERE, "era_auto_dashboard.html")
    open(out_html, "w", encoding="utf-8").write(html)
    log("HTML written: %s (%d bytes)" % (out_html, len(html.encode("utf-8"))))

    if PUBLISH:
        mtag = month                                  # 'YYYY-MM' — refresh in-month, new row per month
        task_ids = ["ERA_%s_ebay_return_analysis_%s" % (u, mtag) for u in ASSIGNED]
        legacy_ids = ["ebra_%s_ebay_return_analysis_%s" % (u, mtag) for u in ASSIGNED]  # retire the old ebra-coded rows
        task_name = "%s eBay Return Analysis Dashboard — %s (auto monthly)" % (DELIVERABLE_ID, ctx["label"])
        desc = ("%s · %s · eBay Return Analysis Dashboard (%s) — auto monthly refresh. Per-SKU eBay returns "
                "across all stores & marketplaces: %d SKUs returned, %d returns, blended rate %.1f%%, refund "
                "£%.2f, return cost, ads (CPC+CPS), negative feedback, open cases, stock. In-month date-range presets."
                % (REQUIREMENT_ID, PHASE, ctx["label"], stats["n"], stats["returns"],
                   (stats["blended"] or 0) * 100, stats["refund"]))
        rows = [(PROJECT_NAME, PROJECT_CODE, task_name, tid, "Development", "Abiraj", u,
                 ASSIGNED_USER_TEAM, html, desc, 1, 1, "released")
                for u, tid in zip(ASSIGNED, task_ids)]
        try:
            with psycopg2.connect(**WH) as conn:      # one transaction; auto-rollback on exception
                with conn.cursor() as pc:
                    pc.execute("DELETE FROM tech_team_outputs.ph_task WHERE task_id = ANY(%s)", (task_ids + legacy_ids,))
                    if pc.rowcount:
                        log("refreshed: removed %d pre-existing row(s) (incl. retired ebra rows) for %s" % (pc.rowcount, mtag))
                    execute_values(pc, """INSERT INTO tech_team_outputs.ph_task
                        (project_name,project_code,task_name,task_id,team,developer,assigned_user,assigned_user_team,
                         html_content,description,phase_level,version_level,version_status,created_at,updated_at)
                        VALUES %s RETURNING id,assigned_user""", rows,
                        template="(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),now())")
                    pub = pc.fetchall()
                    if len(pub) != len(ASSIGNED):
                        raise RuntimeError("inserted %d rows, expected %d - rolling back" % (len(pub), len(ASSIGNED)))
                    # md5-verify every stored payload BEFORE the commit
                    bad = []
                    for rid, user in pub:
                        pc.execute("SELECT md5(html_content) FROM tech_team_outputs.ph_task WHERE id=%s", (rid,))
                        if pc.fetchone()[0] != html_md5: bad.append((rid, user))
                    if bad:
                        raise RuntimeError("md5 verify failed pre-commit %s - rolling back" % bad)
                    for rid, user in pub:
                        log("published id=%s user=%s md5=%s" % (rid, user, html_md5[:8]))
        except Exception as e:
            die("publish failed, transaction rolled back: %s" % e)
        log("published to ph_task (%d users) as project_code=%s, %d payloads md5-verified."
            % (len(ASSIGNED), PROJECT_CODE, len(ASSIGNED)))
    else:
        log("--no-publish: skipped ph_task write.")

    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    act = ("PUBLISHED to %d users" % len(ASSIGNED)) if PUBLISH else "built only (no publish)"
    line = ("[%s]  OK  |  %s  |  %d SKUs / %d returns  |  refund £%.2f  |  %s\n"
            % (stamp, ctx["label"], stats["n"], stats["returns"], stats["refund"], act))
    with open(os.path.join(HERE, "era_status.txt"), "a", encoding="utf-8") as f:
        f.write(line)
    log("status recorded -> era_status.txt")
    log("done.")

if __name__ == "__main__":
    main()
