#!/usr/bin/env python3
"""
epns_weekly_run.py — REQ-22-D02 weekly automation for eBay Product Net Sales.

End-to-end, fail-closed:
  1. Build settled per-order Net Sales data from LIVE ledsone (read-only, direct psycopg2).
  2. Gates: refuse to publish on too-few rows or a collapse vs the last good run.
  3. Render the static-first portal HTML (+ Excel) deliverables.
  4. Guarded publish to tech_team_outputs.ph_task for the ebay_priors audience
     (SELECT-then-INSERT/UPDATE per user, always sets assigned_user_team='ebay_priors').
  5. Write a status file; pop a Desktop alert on failure.

Credentials come only from env (source epns_secrets.bat first) — never committed.
Run:  run_epns_weekly.bat   (or: set env, then `python epns_weekly_run.py`)
"""
import os, sys, json, hashlib, traceback, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
SQLDIR = os.path.join(PROJ, "sql", "REQ-22_ebay-product-net-sales")
OUTDIR = os.path.join(PROJ, "evidence", "final_outputs", "REQ-22_ebay-product-net-sales")
sys.path.insert(0, SQLDIR)

PORTAL_HTML = os.path.join(OUTDIR, "REQ-22-D01_ph_task.html")
XLSX        = os.path.join(OUTDIR, "REQ-22-D01_ebay_product_net_sales.xlsx")
STATUS      = os.path.join(HERE, "epns_status.txt")
LASTGOOD    = os.path.join(HERE, "epns_last_good.json")

AUDIENCE = ["Thinesh", "Jarsini", "kobiga", "powsteena", "Sharmilan", "Sivajitha"]
ASSIGNED_TEAM = "ebay_priors"
PROJECT_NAME  = "eBay Product Net Sales"
PROJECT_CODE  = "epns"
TASK_NAME     = "REQ-22-D01 eBay Product Net Sales — per-order Net Sales (NNV), settled orders, last 30 days (12 cols)"
TEAM, DEVELOPER = "Development", "Abiraj"
DESCRIPTION   = ("Per-eBay-order Net Sales (NNV) for the last 30 days, SETTLED orders only. "
                 "NNV = Gross - Final Value Fee - General(AD_FEE). General = Promoted Listings General fee; "
                 "PPC = Advanced/Priority (PREMIUM_AD_FEES) ads. VAT & Product Cost are estimates. "
                 "Read-only from raw ledsone (source_id=2). Per marketplace currency, never blended. Weekly auto-refresh.")

MIN_ROWS      = 1500     # hard floor — a healthy week is ~4,000 settled orders
COLLAPSE_FRAC = 0.60     # refuse if < 60% of the last good row count

def log(m): print(f"[{dt.datetime.now():%Y-%m-%d %H:%M:%S}] {m}", flush=True)

def alert(msg):
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, msg, "EPNS weekly FAILED", 0x10)
    except Exception:
        pass

def write_status(ok, msg):
    with open(STATUS, "w", encoding="utf-8") as f:
        f.write(f"{'OK' if ok else 'FAIL'} {dt.datetime.now():%Y-%m-%d %H:%M:%S}\n{msg}\n")

def publish(html):
    import psycopg2
    pw = os.environ.get("PGPASSWORD")
    if not pw:
        raise SystemExit("PGPASSWORD (warehouse) not set")
    conn = psycopg2.connect(host=os.getenv("WH_PGHOST", "149.28.134.54"),
                            port=os.getenv("WH_PGPORT", "5435"),
                            dbname=os.getenv("WH_PGDATABASE", "order_management_copy"),
                            user=os.getenv("WH_PGUSER", "temp_user"), password=pw, connect_timeout=30)
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            for user in AUDIENCE:
                tid = f"epns_{user}_ebay_product_net_sales"
                cur.execute("SELECT id FROM tech_team_outputs.ph_task WHERE task_id=%s", (tid,))
                row = cur.fetchone()
                if row:
                    cur.execute("""UPDATE tech_team_outputs.ph_task
                        SET html_content=%s, description=%s, task_name=%s, project_name=%s, developer=%s,
                            assigned_user_team=%s, version_level=COALESCE(version_level,0)+1,
                            version_status='released', updated_at=now() WHERE id=%s""",
                        (html, DESCRIPTION, TASK_NAME, PROJECT_NAME, DEVELOPER, ASSIGNED_TEAM, row[0]))
                else:
                    cur.execute("""INSERT INTO tech_team_outputs.ph_task
                        (project_name, project_code, task_name, task_id, team, developer, assigned_user,
                         assigned_user_team, html_content, description, phase_level, version_level, version_status)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,1,1,'released')""",
                        (PROJECT_NAME, PROJECT_CODE, TASK_NAME, tid, TEAM, DEVELOPER, user, ASSIGNED_TEAM, html, DESCRIPTION))
        conn.commit()
    finally:
        conn.close()

def main():
    import epns_build_d01 as b
    import render_epns_portal as p

    log("fetching settled rows from live ledsone (read-only)...")
    rows = b.fetch_rows()
    n = len(rows)
    log(f"rows: {n}")

    # ---- fail-closed gates ----
    if n < MIN_ROWS:
        raise SystemExit(f"GATE row-floor: {n} < {MIN_ROWS} — refusing to publish")
    if os.path.exists(LASTGOOD):
        try:
            last = json.load(open(LASTGOOD)).get("rows", 0)
            if last and n < last * COLLAPSE_FRAC:
                raise SystemExit(f"GATE collapse: {n} < {COLLAPSE_FRAC:.0%} of last good {last} — refusing")
        except SystemExit:
            raise
        except Exception:
            pass

    log("rendering portal HTML + Excel...")
    p.render_portal(list(rows), PORTAL_HTML)
    try:
        b.write_workbook([dict(r) for r in rows], XLSX)
    except Exception as e:
        log(f"warn: xlsx render skipped ({e})")

    html = open(PORTAL_HTML, encoding="utf-8").read()
    md5 = hashlib.md5(html.encode()).hexdigest()
    log(f"publishing to ph_task ({len(html):,} chars, md5 {md5[:8]}) for {len(AUDIENCE)} users...")
    publish(html)

    json.dump({"rows": n, "md5": md5, "at": f"{dt.datetime.now():%Y-%m-%d %H:%M:%S}"},
              open(LASTGOOD, "w"))
    write_status(True, f"{n} rows published to ph_task (ebay_priors, {len(AUDIENCE)} users)")
    log("DONE.")

if __name__ == "__main__":
    try:
        main()
    except SystemExit as e:
        write_status(False, str(e)); alert(f"EPNS weekly: {e}"); log(f"ABORT: {e}"); sys.exit(1)
    except Exception:
        tb = traceback.format_exc()
        write_status(False, tb); alert("EPNS weekly crashed — see epns_status.txt"); log(tb); sys.exit(1)
