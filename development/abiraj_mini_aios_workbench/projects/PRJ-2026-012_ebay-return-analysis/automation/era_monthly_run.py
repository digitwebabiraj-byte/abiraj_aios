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

Connections (env vars; passwords NEVER hardcoded — provided by the git-ignored era_secrets.bat):
  Ledsone (READ, the data):        LED_PGHOST LED_PGPORT LED_PGDATABASE LED_PGUSER LED_PGPASSWORD
  Warehouse (WRITE, ph_task only): PGHOST PGPORT PGDATABASE PGUSER PGPASSWORD

Flags:  --no-publish   (build the HTML only; do NOT write ph_task)
Usage:  python era_monthly_run.py [--no-publish] [YYYY-MM]
Requires: build_returns_live_html.py + build_returns_html.py + the mockup xlsx (in evidence/final_outputs).
"""
import os, sys, calendar
from datetime import date, timedelta, datetime
import psycopg2
from psycopg2.extras import execute_values

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
FINAL_DIR = os.path.join(PROJECT, "evidence", "final_outputs", "REQ-14_ebay-return-analysis")
MOCKUP = os.path.join(FINAL_DIR, "eBay_Return_Analysis_June2026.xlsx")
sys.path.insert(0, FINAL_DIR)
import build_returns_live_html as BL   # generate(), month_ctx()

PUBLISH = "--no-publish" not in sys.argv
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
        raise SystemExit("[ERA] LEDSONE creds not set — populate era_secrets.bat (LED_PG*).")

    led = psycopg2.connect(**LED); led.set_session(readonly=True, autocommit=True)
    html, views_data, cache, stats = BL.generate(month, led, MOCKUP)
    led.close()
    log("built %s: %d SKUs / %d returns / £%.2f refund / £%.2f ad spend / ACOS %.1f%% / ROAS %.2fx"
        % (stats["month"], stats["n"], stats["returns"], stats["refund"], stats["spend"],
           (stats["acos"] or 0) * 100, stats["roas"] or 0))

    out_html = os.path.join(HERE, "era_auto_dashboard.html")
    open(out_html, "w", encoding="utf-8").write(html)
    log("HTML written: %s (%d bytes)" % (out_html, len(html.encode("utf-8"))))

    if PUBLISH:
        if not WH["password"]:
            raise SystemExit("[ERA] warehouse PGPASSWORD not set — cannot publish.")
        mtag = month                                    # 'YYYY-MM' — refresh in-month, new row per month
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
        with psycopg2.connect(**WH) as conn:
            with conn.cursor() as pc:
                pc.execute("DELETE FROM tech_team_outputs.ph_task WHERE task_id = ANY(%s)", (task_ids + legacy_ids,))
                if pc.rowcount:
                    log("refreshed: removed %d pre-existing row(s) (incl. retired ebra rows) for %s" % (pc.rowcount, mtag))
                execute_values(pc, """INSERT INTO tech_team_outputs.ph_task
                    (project_name,project_code,task_name,task_id,team,developer,assigned_user,assigned_user_team,
                     html_content,description,phase_level,version_level,version_status,created_at,updated_at)
                    VALUES %s RETURNING id,assigned_user""", rows,
                    template="(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),now())")
                for r in pc.fetchall():
                    log("published id=%s user=%s" % (r[0], r[1]))
        log("published to ph_task (%d users) as project_code=%s." % (len(ASSIGNED), PROJECT_CODE))
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
