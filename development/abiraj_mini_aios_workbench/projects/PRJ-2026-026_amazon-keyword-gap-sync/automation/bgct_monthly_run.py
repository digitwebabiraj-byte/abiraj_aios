# -*- coding: utf-8 -*-
"""
REQ-30-D03 - monthly unattended refresh of the BGCT Amazon Keyword Gap report.

Rebuilds the payload from live data, re-renders the single dashboard, and refreshes ph_task id 980
in place (guarded, version-bumped, md5-verified).

FAIL-CLOSED: on any bad pull it refuses to publish, leaves the last good row untouched, writes a
FAILED status and exits non-zero so the wrapper raises a Desktop alert. A stale-but-correct report
beats a fresh wrong one. Read-only on all source data; the only write is the guarded ph_task
refresh. Credentials come from the environment (run_bgct_monthly.bat / the shared global store).

+-------------------------------------------------------------------------------------------------+
| WHY THERE IS NO MINIMUM ON THE GAP COUNT - read this before "fixing" it                          |
| The other fleet jobs gate on their row count (EPPR: refuse if < 8,000 listings). Copying that     |
| here would be wrong. This report's row count is a BACKLOG, not a universe: every keyword          |
| Thuwaraga adds to a listing REMOVES a row. 136 gaps today, and if she does the work it trends to  |
| zero - which is the project SUCCEEDING. A MIN_GAPS floor would start failing the automation at    |
| exactly the moment it worked, and would train whoever reads the alerts to ignore them.            |
| So the gates below are on the STABLE universe (her 776-bulb catalogue) and on the integrity of    |
| the accounting - never on how much work is left.                                                  |
+-------------------------------------------------------------------------------------------------+
"""
import os, sys, io, json, datetime, hashlib, subprocess, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.abspath(os.path.join(HERE, ".."))
SQLDIR = os.path.join(PROJECT, "sql", "REQ-30_amazon-keyword-gap-sync")

BUILD = os.path.join(SQLDIR, "build_bgct_d01.py")
RENDER = os.path.join(SQLDIR, "render_bgct_dashboard.py")
PUBLISH = os.path.join(HERE, "publish_bgct_ph_task.py")
PAYLOAD = os.path.join(SQLDIR, "bgct_payload.json")
HTML = os.path.join(PROJECT, "evidence", "final_outputs", "REQ-30_amazon-keyword-gap-sync",
                    "REQ-30_bgct_keyword_dashboard.html")

STATUS = os.path.join(HERE, "bgct_status.txt")
LASTGOOD = os.path.join(HERE, "bgct_last_good.json")
LOG = os.path.join(HERE, "bgct_run.log")

PH_TASK_ID = 980            # OUR row. The publisher refuses anything whose project_code/task_id differ.

MIN_CATALOGUE = 500         # her Bulbs category is ~776; refuse if the portfolio collapses
MIN_TOP_MOVERS = 1          # no best sellers => nothing can supply keywords => report is meaningless
COLLAPSE = 0.60             # refuse if the catalogue drops below 60% of the last good run
MIN_HTML = 150_000          # baseline ~411 KB; a truncated render must never reach the portal


def log(msg):
    line = "%s  %s" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg)
    print(line)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def write_status(state, detail):
    with open(STATUS, "w", encoding="utf-8") as f:
        f.write("%s | %s | %s\n" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    state, detail))


def load_last_good():
    try:
        with open(LASTGOOD, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def run(script, *args):
    """Run a step as a subprocess and log its FULL output.

    Never filter this. A previous session grepped a build's stdout and missed a crash that the
    unfiltered output showed plainly - the run 'looked' fine because the interesting line was
    filtered away. If it is worth running unattended it is worth logging in full.
    """
    cmd = [sys.executable, script] + list(args)
    log("RUN %s" % " ".join(os.path.basename(c) for c in cmd))
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       cwd=PROJECT)
    for line in (r.stdout or "").splitlines():
        log("   | %s" % line)
    for line in (r.stderr or "").splitlines():
        log("  !| %s" % line)
    if r.returncode != 0:
        raise RuntimeError("%s exited %d" % (os.path.basename(script), r.returncode))
    return r


def gates(p, prev):
    """Every check that must pass before anything is published. Raises on the first failure."""
    cov = p.get("coverage") or {}
    total = int(cov.get("total") or 0)
    buckets = {k: v for k, v in cov.items() if k != "total"}

    if total == 0:
        raise RuntimeError("GATE FAIL: catalogue is empty - not publishing")
    if total < MIN_CATALOGUE:
        raise RuntimeError("GATE FAIL: catalogue %d < MIN_CATALOGUE %d - not publishing"
                           % (total, MIN_CATALOGUE))
    if sum(buckets.values()) != total:
        raise RuntimeError("GATE FAIL: buckets sum to %d but catalogue is %d - the accounting does "
                           "not tie, so some bulbs are unaccounted for" % (sum(buckets.values()), total))
    prev_total = int((prev.get("catalogue") or 0))
    if prev_total and total < COLLAPSE * prev_total:
        raise RuntimeError("GATE FAIL: catalogue %d < %.0f%% of last good %d - not publishing"
                           % (total, COLLAPSE * 100, prev_total))

    tm = int(cov.get("top_moving") or 0)
    if tm < MIN_TOP_MOVERS:
        raise RuntimeError("GATE FAIL: %d Top-Moving ASINs - nothing can supply keywords" % tm)

    # --- SQP coverage -----------------------------------------------------------------------
    # Amazon delivers each account's search data on its own schedule, and DCVOLTAGE is chronically
    # thinner than LEDSone (measured 2026-08-19: 0/3/3 weeks vs 4/4/3 for the same window). Thin is
    # tolerated and disclosed on the dashboard. Two things are NOT tolerated: every account empty,
    # and an account that had data last month silently arriving with none this month.
    sqp = p.get("sqp_coverage") or {}
    if sqp:
        live = {b: int(c.get("min_weeks") or 0) for b, c in sqp.items()}
        got = {b: sum((c.get("weeks_by_month") or {}).values()) for b, c in sqp.items()}
        if not any(got.values()):
            raise RuntimeError("GATE FAIL: no SQP weeks for ANY account in the window - not publishing")
        for b, weeks in (prev.get("sqp_weeks") or {}).items():
            if weeks > 0 and got.get(b, 0) == 0:
                raise RuntimeError("GATE FAIL: account %s had %d SQP weeks last run and has 0 now - "
                                   "that is an account silently dropping out, not a quiet month" % (b, weeks))
        log("SQP weeks this run: %s (min weeks/month: %s)" % (got, live))

    log("gates PASS (catalogue=%d, last_good=%s, top_movers=%d, buckets tie)"
        % (total, prev_total or "-", tm))
    return total


def main():
    log("=== BGCT monthly run START ===")
    try:
        if not os.getenv("PGPASSWORD"):
            raise RuntimeError("PGPASSWORD is not set - refusing to run (secrets come from the "
                               "environment, never from tracked code)")

        run(BUILD)                                    # rebuild the payload from live data
        with open(PAYLOAD, encoding="utf-8") as f:
            p = json.load(f)

        prev = load_last_good()
        total = gates(p, prev)                        # <- refuses before anything is rendered

        run(RENDER)                                   # single dashboard, rebuilt from that payload
        size = os.path.getsize(HTML) if os.path.exists(HTML) else 0
        if size < MIN_HTML:
            raise RuntimeError("GATE FAIL: dashboard is %d bytes (< %d) - truncated render, "
                               "not publishing" % (size, MIN_HTML))

        run(PUBLISH, "--update", str(PH_TASK_ID))     # guarded; it md5-verifies the read-back itself

        # Match the PUBLISHER's read exactly, or this md5 is worthless for verification.
        # It reads text mode (universal newlines collapse the file's 723 CRLF pairs to LF) and
        # encodes utf-8; a binary read here gives a different digest that can never equal the one
        # stored in ph_task, which is the opposite of what a last-good record is for.
        md5 = hashlib.md5(io.open(HTML, encoding="utf-8").read().encode()).hexdigest()
        gaps = sum(1 for r in p.get("part_b", []) if r.get("add_target") != "none")
        json.dump({"catalogue": total,
                   "gaps": gaps,
                   "top_moving": (p.get("coverage") or {}).get("top_moving"),
                   "html_bytes": size,
                   "md5": md5,
                   "sqp_weeks": {b: sum((c.get("weeks_by_month") or {}).values())
                                 for b, c in (p.get("sqp_coverage") or {}).items()},
                   "reference_date": p.get("reference_date"),
                   "when": datetime.datetime.now().isoformat()},
                  open(LASTGOOD, "w", encoding="utf-8"), indent=1)

        write_status("OK", "published ph_task %d | %d bulbs | %d gaps | md5 %s"
                     % (PH_TASK_ID, total, gaps, md5[:8]))
        log("=== BGCT monthly run OK (%d bulbs, %d gaps, ph_task %d) ===" % (total, gaps, PH_TASK_ID))
        return 0
    except Exception as e:
        log("FAILED: %s" % e)
        log(traceback.format_exc())
        write_status("FAILED", str(e).splitlines()[0])
        return 1


if __name__ == "__main__":
    sys.exit(main())
