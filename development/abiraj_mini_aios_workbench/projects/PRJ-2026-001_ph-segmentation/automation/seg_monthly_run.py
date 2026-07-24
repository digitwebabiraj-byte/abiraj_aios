# -*- coding: utf-8 -*-
"""
PH ASIN Segmentation - AUTONOMOUS monthly run (REQ-05 automation).

Runs on the 3rd of each month. Recomputes the whole portfolio READ-ONLY from the live warehouse
(public.traffic_data + public.order_transaction), rebuilds the leader + per-PH dashboards using the
signed-off toolkit templates, and publishes them to tech_team_outputs.ph_task.

Owner-confirmed design (see TASK_REGISTER.md, 2026-07-24):
  * Window   : NORMAL roll-forward, last 4 complete Saturday-weeks vs previous 4 (rn 1..4 / 5..8 / 9..12).
  * Rule     : COUNT-based conversion (matches what is already live) - a refresh, not a rule change.
  * Roster   : DYNAMIC from sql/00 + sql/04 each run (never the frozen July NAMES/ALLOC maps).
  * Departed : REPORTED, never auto-deleted.
  * Grain    : NEW ROW PER MONTH, task_id ph-asin-YYYY-MM-<PH> (+ leader). Re-run of the same month
               = DELETE that month's rows by task_id prefix, then INSERT - never a blind insert.

ONE database: the warehouse temp_user connection is both the data source (public.*, read-only) and the
publish target (tech_team_outputs.ph_task). No second DB, no MCP (a scheduled task has no MCP session).

FAILS CLOSED: every gate runs before any write. Any failure -> exit 2, nothing published.

Flags:  --dry-run / --no-publish   (recompute + build + validate; write NOTHING to ph_task)
        --month YYYY-MM            (override the reporting-month label; default = current month)
Usage:  python seg_monthly_run.py [--dry-run] [--month YYYY-MM]

Status: BUILT 2026-07-24, NOT YET dry-run-verified end-to-end (30 PHs) - see TASK_REGISTER.
        Do NOT register the scheduled task until a clean full dry-run has been reviewed.
"""
import os, sys, json, time, hashlib, calendar
import datetime as dt
from collections import Counter
import psycopg2

HERE     = os.path.dirname(os.path.abspath(__file__))
PROJECT  = os.path.dirname(HERE)
TOOLKIT  = os.path.join(PROJECT, "capability", "2026-07-10_monthly_rebuild_toolkit")
SQLDIR   = os.path.join(TOOLKIT, "sql")
TMPLDIR  = os.path.join(TOOLKIT, "tmpl")
BACKUPDIR= os.path.join(HERE, "backups")
LAST_GOOD= os.path.join(HERE, "seg_last_good.json")   # git-ignored collapse baseline
STATUS   = os.path.join(HERE, "seg_status.txt")

PUBLISH   = not ("--dry-run" in sys.argv or "--no-publish" in sys.argv)
MONTH_ARG = None
if "--month" in sys.argv:
    try: MONTH_ARG = sys.argv[sys.argv.index("--month") + 1]
    except IndexError: pass

# ---- governance identity (ph_task) ----
PROJECT_NAME = "PH ASIN Segmentation"
PROJECT_CODE = "ph-asin"
TEAM, DEVELOPER = "Development", "Abiraj"
ASSIGNED_USER_TEAM = "ph_priors"          # REQUIRED - missing = the card-team gap (not in sample DDL)

# ---- fail-closed gate thresholds ----
MIN_TOTAL = int(os.getenv("SEG_MIN_TOTAL", "5000"))   # catastrophic floor (live ~9,900-10,100)
MIN_PHS   = int(os.getenv("SEG_MIN_PHS",   "20"))     # roster floor (live 30)
MAX_DROP  = float(os.getenv("SEG_MAX_DROP", "0.40"))  # collapse guard vs last good run
PH_TIMEOUT_MS = int(os.getenv("SEG_PH_TIMEOUT_MS", "280000"))  # per-PH statement timeout

WH = dict(host=os.getenv("PGHOST", "149.28.134.54"), port=os.getenv("PGPORT", "5435"),
          dbname=os.getenv("PGDATABASE", "order_management_copy"),
          user=os.getenv("PGUSER", "temp_user"), password=os.getenv("PGPASSWORD"))

SEG_ORDER = ["HHH", "HHL", "HLH", "LHH", "LLH", "LLL"]


def log(m): print("[SEG] " + m, flush=True)

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
    """Retry the shared temp_user pool - it intermittently refuses connections (confirmed 2026-07-24)."""
    last = None
    for attempt in range(1, 6):
        try:
            c = psycopg2.connect(connect_timeout=20, **WH)
            c.set_client_encoding("UTF8")
            return c
        except Exception as e:
            last = str(e).strip().splitlines()[-1]
            log("  warehouse connect attempt %d/5 failed: %s" % (attempt, last))
            time.sleep(8)
    die("cannot connect to the warehouse after 5 attempts: %s" % last)


def load_sql(name):
    with open(os.path.join(SQLDIR, name), encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------- collapse guard
def collapse_guard(total):
    if not os.path.exists(LAST_GOOD):
        return
    try:
        prev = json.load(open(LAST_GOOD, encoding="utf-8")).get("total")
    except (ValueError, OSError):
        log("WARN: %s unreadable - skipping collapse check" % LAST_GOOD); return
    if prev and total < prev * (1 - MAX_DROP):
        die("total collapsed %d -> %d (>%.0f%% drop vs last good run)" % (prev, total, MAX_DROP * 100))
    if prev:
        log("collapse guard OK: total %d vs last good %d" % (total, prev))

def record_good(total, per_ph):
    try:
        json.dump({"total": total, "phs": len(per_ph)}, open(LAST_GOOD, "w", encoding="utf-8"), indent=1)
    except OSError as e:
        log("WARN: could not write %s (%s)" % (LAST_GOOD, e))


# ---------------------------------------------------------------- data layer
def roster(conn):
    """sql/00 - the dynamic PH roster (holders with which_channel=1 Amazon products)."""
    with conn.cursor() as cur:
        cur.execute(load_sql("00_roster_names.sql"))
        names = [r[1] for r in cur.fetchall() if (r[2] or 0) > 0]
    if len(names) < MIN_PHS:
        die("roster has only %d PHs (< floor %d) - broken roster pull" % (len(names), MIN_PHS))
    log("roster: %d portfolio holders" % len(names))
    return names

def allocations(conn):
    """sql/04 - the Allocated card counts per PH."""
    with conn.cursor() as cur:
        cur.execute(load_sql("04_alloc_counts.sql"))
        return {r[0]: int(r[1]) for r in cur.fetchall()}

def recompute_ph(conn, name, sql01):
    """Run sql/01 for one PH with its own timeout + retry. Returns (rows, cats).
    NOTE: the utharsika category-split fallback (sql/02) is a KNOWN follow-up - the first full
    dry-run confirms whether any PH exceeds PH_TIMEOUT_MS on a normal (single) window before we
    wire the split. Until then a per-PH timeout is a fail-closed abort, not a silent skip."""
    q = sql01.replace("__PHNAME__", name.replace("'", "''"))
    for attempt in range(1, 4):
        try:
            with conn.cursor() as cur:
                cur.execute("SET statement_timeout=%d" % PH_TIMEOUT_MS)
                cur.execute(q)
                nrows, rows, cats = cur.fetchone()
            rows = rows or []; cats = cats or []
            assert all(x[0] == name for x in rows), "a row is labelled for another PH"
            return rows, cats
        except Exception as e:
            conn.rollback()
            msg = str(e).strip().splitlines()[-1]
            log("  %s recompute attempt %d/3 failed: %s" % (name, attempt, msg))
            if attempt < 3:
                time.sleep(5)
    die("recompute failed for PH '%s' after 3 attempts" % name)


# ---------------------------------------------------------------- assembly
def build_html(period, generated, alloc, phs_order, rows, cats, single_ph=None):
    """Reproduce the toolkit assemblers exactly: html = prefix + json(D) + suffix.
    single_ph=None -> leader (all PHs, tmpl_suffix). single_ph=name -> that PH only (tmpl_suffix_single)."""
    prefix = open(os.path.join(TMPLDIR, "tmpl_prefix.txt"), encoding="utf-8").read()
    if single_ph is None:
        suffix = open(os.path.join(TMPLDIR, "tmpl_suffix.txt"), encoding="utf-8").read()
        idx = {n: i for i, n in enumerate(phs_order)}
        rows2 = [[idx[x[0]]] + x[1:] for x in rows]
        cats2 = [[idx[x[0]]] + x[1:] for x in cats]
        D = {"period": period, "generated": generated,
             "alloc": {n: alloc.get(n, 0) for n in phs_order}, "phs": phs_order,
             "rows": rows2, "cats": cats2}
    else:
        suffix = open(os.path.join(TMPLDIR, "tmpl_suffix_single.txt"), encoding="utf-8").read()
        rows2 = [[0] + x[1:] for x in rows]
        cats2 = [[0] + x[1:] for x in cats]
        D = {"period": period, "generated": generated,
             "alloc": {single_ph: alloc.get(single_ph, 0)}, "phs": [single_ph],
             "rows": rows2, "cats": cats2}
    return prefix + json.dumps(D, ensure_ascii=False, separators=(",", ":")) + suffix


# ---------------------------------------------------------------- publish
def publish(conn, month_tag, leader_html, per_ph_html, generated):
    """NEW ROW PER MONTH. Back up this month's existing rows, DELETE them by task_id prefix,
    INSERT the fresh set, md5-verify every payload before commit. One transaction, auto-rollback."""
    prefix = "ph-asin-%s-" % month_tag
    leader_tid = prefix + "LEADER"
    os.makedirs(BACKUPDIR, exist_ok=True)

    payloads = [(leader_tid, "LEADER", leader_html)]
    for ph, html in per_ph_html.items():
        payloads.append((prefix + ph, ph, html))
    want = {tid: hashlib.md5(h.encode("utf-8")).hexdigest() for tid, _, h in payloads}

    try:
        with conn:                                       # one transaction; rollback on any exception
            with conn.cursor() as cur:
                # back up anything already under this month's prefix (re-run safety)
                cur.execute("""SELECT task_id, html_content FROM tech_team_outputs.ph_task
                               WHERE task_id LIKE %s""", (prefix + "%",))
                existing = cur.fetchall()
                if existing:
                    bpath = os.path.join(BACKUPDIR, "ph_task_%s_backup_%s.json"
                                         % (month_tag, dt.datetime.now().strftime("%Y%m%d_%H%M%S")))
                    json.dump({t: h for t, h in existing}, open(bpath, "w", encoding="utf-8"))
                    log("backed up %d existing '%s' row(s) -> %s" % (len(existing), prefix, bpath))
                    cur.execute("DELETE FROM tech_team_outputs.ph_task WHERE task_id LIKE %s", (prefix + "%",))
                    log("deleted %d pre-existing row(s) for this month (refresh)" % cur.rowcount)

                ins = 0
                for tid, who, html in payloads:
                    name = ("PH ASIN Segmentation - Leader (all PHs)" if who == "LEADER"
                            else "PH ASIN Segmentation - %s" % who)
                    desc = "PH ASIN Segmentation %s (generated %s) - monthly auto refresh." % (month_tag, generated)
                    assigned = "Bietrick" if who == "LEADER" else who
                    cur.execute("""INSERT INTO tech_team_outputs.ph_task
                        (project_name,project_code,task_name,task_id,team,developer,assigned_user,
                         assigned_user_team,html_content,description,phase_level,version_level,
                         version_status,created_at,updated_at)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,1,1,'released',now(),now())""",
                        (PROJECT_NAME, PROJECT_CODE, name, tid, TEAM, DEVELOPER, assigned,
                         ASSIGNED_USER_TEAM, html, desc))
                    ins += 1

                # md5-verify every stored payload BEFORE commit
                cur.execute("""SELECT task_id, md5(html_content) FROM tech_team_outputs.ph_task
                               WHERE task_id LIKE %s""", (prefix + "%",))
                got = dict(cur.fetchall())
                bad = [tid for tid in want if got.get(tid) != want[tid]]
                if bad:
                    raise RuntimeError("md5 verify failed pre-commit for %s - rolling back" % bad[:5])
                log("inserted %d rows, all md5-verified" % ins)
    except Exception as e:
        die("publish failed, transaction rolled back: %s" % str(e).strip().splitlines()[-1])


# ---------------------------------------------------------------- main
def main():
    if not WH["password"]:
        die("PGPASSWORD not set - see 05_documentation/capability/shared_db_credentials/")

    today = dt.date.today()
    month_tag = MONTH_ARG or ("%04d-%02d" % (today.year, today.month))
    generated = today.strftime("%d %b %Y")
    log("reporting month = %s · generated %s · publish=%s" % (month_tag, generated, PUBLISH))

    conn = connect()
    conn.set_session(readonly=True)          # read-only for the whole recompute
    sql01 = load_sql("01_recompute_per_ph.sql")
    names = roster(conn)
    alloc = allocations(conn)

    all_rows, all_cats, per_ph_rows = [], [], {}
    t0 = time.time()
    for i, ph in enumerate(names, 1):
        rows, cats = recompute_ph(conn, ph, sql01)
        per_ph_rows[ph] = (rows, cats)
        all_rows += rows; all_cats += cats
        log("  [%2d/%2d] %-16s rows=%-5d cats=%-3d (%.0fs elapsed)"
            % (i, len(names), ph, len(rows), len(cats), time.time() - t0))

    # ---- VALIDATION GATES (fail closed, before any write) ----
    total = len(all_rows)
    if total < MIN_TOTAL:            die("only %d ASIN rows (< floor %d) - broken pull" % (total, MIN_TOTAL))
    collapse_guard(total)
    seg = Counter(x[2] for x in all_rows)
    if sum(seg.values()) != total:   die("segment tally %d != total %d" % (sum(seg.values()), total))
    bad_seg = set(seg) - set(SEG_ORDER)
    if bad_seg:                      die("unexpected segment code(s): %s" % bad_seg)
    missing = [n for n in names if n not in per_ph_rows or not per_ph_rows[n][0]]
    if missing:                      die("no rows produced for PH(s): %s" % missing[:5])
    conn.rollback()                  # close the read-only view cleanly before publishing
    log("validation PASSED: total=%d | %s" % (total, " ".join("%s=%d" % (k, seg[k]) for k in SEG_ORDER)))
    log("movement: %s" % dict(Counter(x[3] for x in all_rows)))

    # departed-holder report (never auto-deleted)
    # (a holder with a prior-month ph_task row but absent from today's roster)
    with conn.cursor() as cur:
        cur.execute("""SELECT DISTINCT assigned_user FROM tech_team_outputs.ph_task
                       WHERE project_code=%s AND assigned_user <> 'Bietrick'""", (PROJECT_CODE,))
        known = {r[0] for r in cur.fetchall()}
    departed = sorted(known - set(names))
    if departed:
        log("DEPARTED (still have ph_task rows, review + delete manually): %s" % departed)

    # ---- assemble ----
    phs_order = sorted(names, key=str.lower)
    leader_html = build_html(month_tag, generated, alloc, phs_order, all_rows, all_cats, single_ph=None)
    per_ph_html = {}
    for ph, (rows, cats) in per_ph_rows.items():
        per_ph_html[ph] = build_html(month_tag, generated, alloc, phs_order, rows, cats, single_ph=ph)
    for label, html in [("leader", leader_html)] + [(k, v) for k, v in list(per_ph_html.items())[:1]]:
        if "const D=" not in html or len(html) < 20000:
            die("assembly looks broken for %s (%d bytes)" % (label, len(html)))
    log("assembled leader (%d bytes) + %d per-PH dashboards" % (len(leader_html), len(per_ph_html)))

    if not PUBLISH:
        log("--dry-run: recomputed, validated and assembled; wrote NOTHING to ph_task.")
        _status("OK(dry-run)", "%d ASINs / %d PHs | %s | built only"
                % (total, len(names), " ".join("%s=%d" % (k, seg[k]) for k in SEG_ORDER)))
        conn.close(); log("done."); return

    publish(conn, month_tag, leader_html, per_ph_html, generated)
    record_good(total, per_ph_rows)
    _status("OK", "%d ASINs / %d PHs | %s | PUBLISHED %d rows"
            % (total, len(names), " ".join("%s=%d" % (k, seg[k]) for k in SEG_ORDER), len(per_ph_html) + 1))
    conn.close(); log("done.")


if __name__ == "__main__":
    main()
