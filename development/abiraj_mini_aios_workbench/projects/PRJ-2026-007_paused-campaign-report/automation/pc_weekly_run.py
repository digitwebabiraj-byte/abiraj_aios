# -*- coding: utf-8 -*-
"""
PC - Paused Campaign Report (Utharsika) - AUTONOMOUS weekly run (REQ-09 automation).

Every Wednesday: list Utharsika's Amazon ad targets that PPC automation paused and that are STILL
paused today, READ-ONLY from the live warehouse, and refresh the polished dashboard in ph_task.

The canonical hand-finished dashboard (Utharsika_Paused_Campaigns_Report.html) is data-driven: its
ROWS come from an embedded <script id="payload"> JSON block and every KPI is computed in the browser
from ROWS. So this runner keeps the EXACT same look and only re-injects, per run:
  * the payload rows (11 fields per row - see derive_row)
  * const RUN (run date), TOTAL_PAUSES (all automation pauses), WINDOW (perf window)
The canonical HTML is read as a TEMPLATE, never modified.

The signed-off SQL already uses CURRENT_DATE (Days Paused, still-paused) so NO date parameterization
is needed - it is run-date safe as written.

Publish grain = WEEKLY REPLACE in place (task_id PC_utharsika_paused_campaigns_dashboard-V1, id 215),
backup-first, md5-verified. ONE warehouse connection, read data + publish. FAILS CLOSED.

Flags:  --dry-run / --no-publish   (build + validate, write NOTHING to ph_task)
Usage:  python pc_weekly_run.py [--dry-run]

Status: BUILT 2026-07-24 - dry-run validate before scheduling.
"""
import os, sys, re, json, time, hashlib
import datetime as dt
from decimal import Decimal
import psycopg2

HERE      = os.path.dirname(os.path.abspath(__file__))
PROJECT   = os.path.dirname(HERE)
SQL_PATH  = os.path.join(PROJECT, "sql", "REQ-09_paused-campaign-report", "generate_report.sql")
TEMPLATE  = os.path.join(PROJECT, "evidence", "final_outputs", "REQ-09_paused-campaign-report",
                         "Utharsika_Paused_Campaigns_Report.html")
LAST_GOOD = os.path.join(HERE, "pc_last_good.json")
STATUS    = os.path.join(HERE, "pc_status.txt")
HTML_OUT  = os.path.join(HERE, "pc_dashboard.html")

PUBLISH = not ("--dry-run" in sys.argv or "--no-publish" in sys.argv)

PROJECT_NAME = "Paused Campaign Report - Utharsika (Amazon PPC automation pauses still active)"
PROJECT_CODE = "PC"
TASK_ID      = "PC_utharsika_paused_campaigns_dashboard-V1"
TASK_NAME    = "PC - Paused Campaign Report - Utharsika (weekly auto)"
TEAM, DEVELOPER = "Development", "Abiraj"
ASSIGNED_USER, ASSIGNED_USER_TEAM = "utharsika", "ph_priors"

MIN_ROWS = int(os.getenv("PC_MIN_ROWS", "1"))          # never publish 0 over a good report
MAX_DROP = float(os.getenv("PC_MAX_DROP", "0.50"))     # pauses are volatile -> generous collapse band
SQL_TIMEOUT_MS = int(os.getenv("PC_SQL_TIMEOUT_MS", "120000"))

WH = dict(host=os.getenv("PGHOST", "149.28.134.54"), port=os.getenv("PGPORT", "5435"),
          dbname=os.getenv("PGDATABASE", "order_management_copy"),
          user=os.getenv("PGUSER", "temp_user"), password=os.getenv("PGPASSWORD"))

RULE_LABEL   = {1: "Rule 1 · ACOS", 2: "Rule 2 · Zero orders + spend", 3: "Rule 3 · Spend based"}
RULE_SUMMARY = {1: "High ACOS — spend outrunning sales", 2: "Zero orders while spending",
                3: "Orders dried up, spend continued"}


def log(m): print("[PC] " + m, flush=True)

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


# ---------------------------------------------------------------- reason -> chips (per rule)
def _num(pat, s, d=None):
    m = re.search(pat, s)
    return m.group(1) if m else d

def derive_row(cn, ag, asin, sku, reason, pause_date, days):
    m = re.match(r"\s*Rule\s*(\d)", reason or "")
    rn = int(m.group(1)) if m else 0
    chips = []
    try:
        if rn == 1:
            acos = _num(r"ACOS\s*([\d.]+)%", reason); a7 = _num(r"Last 7 Days ACOS\s*([\d.]+)%", reason)
            orders = _num(r"with\s*(\d+)\s*orders", reason)
            chips = [["ACOS", "%s%%" % acos], ["7-day ACOS", "%s%%" % a7], ["Orders", orders]]
        elif rn == 2:
            price = _num(r"Product Price\s*([\d.]+)", reason); spend = _num(r"Last 30 Days Spend\s*([\d.]+)", reason)
            pct = _num(r"\(([\d.]+)% of product price", reason); orders = _num(r"with\s*(\d+)\s*orders", reason)
            chips = [["Spend 30d", "£%s" % spend], ["of £%s" % price, "%s%%" % pct], ["Orders", orders]]
        elif rn == 3:
            price = _num(r"Product Price\s*([\d.]+)", reason); spend = _num(r"Last 7 Days Spend\s*([\d.]+)", reason)
            pct = _num(r"\(([\d.]+)% of product price", reason)
            o30 = _num(r"Last 30 days Orders\s*(\d+)", reason); o7 = _num(r"Last 7 days Orders\s*(\d+)", reason)
            chips = [["Spend 7d", "£%s" % spend], ["of £%s" % price, "%s%%" % pct],
                     ["Orders 30d→7d", "%s→%s" % (o30, o7)]]
    except Exception as e:
        log("  WARN: chip parse failed for %s (rule %s): %s" % (asin, rn, e)); chips = []
    if any("None" in json.dumps(c) for c in chips):
        log("  WARN: a chip value did not parse for %s (rule %s) - reason format may be new" % (asin, rn))
    return {"campaign": cn, "adgroup": ag, "asin": asin, "sku": sku, "reason": reason,
            "pause_date": pause_date, "days": str(days),
            "rule": RULE_LABEL.get(rn, "Rule ?"), "summary": RULE_SUMMARY.get(rn, ""),
            "chips": chips, "rulenum": str(rn)}


# ---------------------------------------------------------------- collapse guard
def collapse_guard(n):
    if not os.path.exists(LAST_GOOD): return
    try: prev = json.load(open(LAST_GOOD, encoding="utf-8")).get("rows")
    except (ValueError, OSError): log("WARN: %s unreadable - skipping collapse check" % LAST_GOOD); return
    if prev and n < prev * (1 - MAX_DROP):
        die("still-paused rows collapsed %d -> %d (>%.0f%% drop vs last good run)" % (prev, n, MAX_DROP * 100))
    if prev: log("collapse guard OK: %d vs last good %d" % (n, prev))

def record_good(n, total):
    try: json.dump({"rows": n, "total_pauses": total}, open(LAST_GOOD, "w", encoding="utf-8"), indent=1)
    except OSError as e: log("WARN: could not write %s (%s)" % (LAST_GOOD, e))


# ---------------------------------------------------------------- template injection
def render(rows, run_date, total_pauses, win_lo, win_hi):
    tmpl = open(TEMPLATE, encoding="utf-8").read()
    payload = json.dumps(rows, ensure_ascii=False)
    run_s = run_date.strftime("%d %b %Y")
    window = "%s – %s" % (win_lo.strftime("%d %b"), win_hi.strftime("%d %b %Y"))
    # 1) payload block
    new, k = re.subn(r'(<script id="payload"[^>]*>).*?(</script>)',
                     lambda m: m.group(1) + payload + m.group(2), tmpl, count=1, flags=re.S)
    if k != 1: die("could not inject payload into the template")
    # 2) the three constants (all on one const RUN=... line)
    new, k1 = re.subn(r"const RUN='[^']*'", "const RUN='%s'" % run_s, new, count=1)
    new, k2 = re.subn(r"TOTAL_PAUSES=\d+", "TOTAL_PAUSES=%d" % total_pauses, new, count=1)
    new, k3 = re.subn(r"WINDOW='[^']*'", "WINDOW='%s'" % window, new, count=1)
    if not (k1 and k2 and k3):
        die("could not update RUN/TOTAL_PAUSES/WINDOW (RUN=%s TOTAL=%s WINDOW=%s)" % (k1, k2, k3))
    return new


# ---------------------------------------------------------------- main
def main():
    if not WH["password"]:
        die("PGPASSWORD not set - see 05_documentation/capability/shared_db_credentials/")
    run_date = dt.date.today()
    log("run_date = %s · publish=%s" % (run_date, PUBLISH))

    sql = open(SQL_PATH, encoding="utf-8").read()
    # TOTAL_PAUSES = count of the pauses CTE (reuse the canonical CTEs, no still-paused filter)
    cte = sql[:sql.index("SELECT uc.campaign_name")]
    total_q = cte + "SELECT count(*) FROM pauses"

    conn = connect(); conn.set_session(readonly=True)
    with conn.cursor() as cur:
        cur.execute("SET statement_timeout=%d" % SQL_TIMEOUT_MS)
        cur.execute(total_q); total_pauses = cur.fetchone()[0]
        cur.execute(sql)
        cols = [d[0] for d in cur.description]
        raw = cur.fetchall()
    conn.rollback()
    log("still-paused rows=%d · total automation pauses=%d" % (len(raw), total_pauses))

    # ---- gates ----
    if len(raw) < MIN_ROWS:  die("0 still-paused rows - refusing to publish an empty report")
    collapse_guard(len(raw))

    # ---- build payload rows ----
    idx = {c: i for i, c in enumerate(cols)}
    def g(r, name):
        v = r[idx[name]]
        if isinstance(v, dt.date): return v.isoformat()
        if isinstance(v, Decimal): return int(v) if v == v.to_integral_value() else float(v)
        return v
    rows, pdates = [], []
    for r in raw:
        pd = r[idx["Campaign Pause Date"]]
        pdates.append(pd if isinstance(pd, dt.date) else dt.date.fromisoformat(str(pd)))
        rows.append(derive_row(g(r, "Campaign Name"), g(r, "Ad Group Name"), g(r, "ASIN"), g(r, "SKU"),
                               g(r, "Pause Reason"), g(r, "Campaign Pause Date"), g(r, "Days Paused")))
    win_lo = min(pdates) - dt.timedelta(days=30)
    win_hi = max(pdates)
    log("window %s .. %s · rules %s" % (win_lo, win_hi,
        {k: sum(1 for x in rows if x["rulenum"] == str(k)) for k in (1, 2, 3)}))

    html = render(rows, run_date, total_pauses, win_lo, win_hi)
    open(HTML_OUT, "w", encoding="utf-8").write(html)
    if "id=\"payload\"" not in html or len(html) < 20000:
        die("rendered HTML looks broken (%d bytes)" % len(html))
    html_md5 = hashlib.md5(html.encode("utf-8")).hexdigest()
    log("built dashboard: %d bytes, md5 %s" % (len(html), html_md5[:8]))

    if not PUBLISH:
        log("--dry-run: recomputed, validated, built; wrote NOTHING to ph_task.")
        _status("OK(dry-run)", "%d still paused / %d total | built only" % (len(raw), total_pauses))
        conn.close(); log("done."); return

    desc = ("Paused Campaign Report (weekly) - Utharsika Amazon ad targets paused by PPC automation "
            "and still paused today: %d of %d total pauses. Reason verbatim, Days Paused = today - pause date."
            % (len(raw), total_pauses))
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, html_content FROM tech_team_outputs.ph_task WHERE task_id=%s", (TASK_ID,))
                got = cur.fetchone()
                if got:
                    open(os.path.join(HERE, "pc_ph_task_backup_%s.html" % dt.datetime.now().strftime("%Y%m%d_%H%M%S")),
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
    record_good(len(raw), total_pauses)
    _status("OK", "%d still paused / %d total | PUBLISHED" % (len(raw), total_pauses))
    log("done.")


if __name__ == "__main__":
    main()
