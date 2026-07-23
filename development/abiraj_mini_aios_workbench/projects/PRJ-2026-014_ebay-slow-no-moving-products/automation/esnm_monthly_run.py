# -*- coding: utf-8 -*-
"""
REQ-16-D02 — eBay Slow Moving & No Moving Products, autonomous monthly refresh.

Runs on the 2nd of each month. Rebuilds all three D01 artefacts from ONE live pull, recalculates
the workbook, and refreshes the live ph_task rows so the portal never shows older numbers than
the files on disk.

    python esnm_monthly_run.py                 # full run, publishes
    python esnm_monthly_run.py --dry-run       # every gate + rebuild, but NO ph_task write
    python esnm_monthly_run.py --anchor 2026-06-30

--------------------------------------------------------------------------------------------
ANCHOR — the whole reason this job is trustworthy
--------------------------------------------------------------------------------------------
The anchor is the **last day of the previous calendar month**, never `today`.

Anchoring on today was recorded as defect H: today is still accumulating orders (~11 units by
09:00 against ~230 for a full day), so a "30-day" window is 29 days plus a stub and the same
report run twice returns different counts — observed 11,156 -> 11,176 listings and Rule 1
8,067 -> 8,065 within one morning. A closed calendar month is complete and reproducible: this
job run on the 2nd, the 3rd or re-run a week later produces the identical dataset.

EPPA hit the same defect and fixed it the same way.

--------------------------------------------------------------------------------------------
FAILS CLOSED
--------------------------------------------------------------------------------------------
Every gate runs BEFORE anything is written. On any failure the previous report survives
untouched, the status file records why, and a desktop alert is raised. A stale-but-correct
report beats a fresh wrong one that tells someone to end 8,000 listings.

Credentials come from the global store via environment variables — never hardcoded.
"""
import os, sys, io, json, time, shutil, subprocess, traceback
from datetime import date, datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, ".."))
SQLDIR = os.path.join(PROJ, "sql", "REQ-16_ebay-slow-no-moving-products")
FINAL = os.path.join(PROJ, "evidence", "final_outputs", "REQ-16_ebay-slow-no-moving-products")
STATUS = os.path.join(HERE, "esnm_status.json")
LOG = os.path.join(HERE, "esnm_run.log")
sys.path.insert(0, SQLDIR)

DRY = ("--dry-run" in sys.argv) or ("--no-publish" in sys.argv)

# ---- fail-closed thresholds (override by env if the portfolio genuinely changes) ----
MIN_LISTINGS = int(os.getenv("ESNM_MIN_LISTINGS", "8000"))   # Jul-2026 reference: 11,176
MAX_DROP     = float(os.getenv("ESNM_MAX_DROP", "0.40"))     # vs the LAST GOOD run
MIN_ACCOUNTS = int(os.getenv("ESNM_MIN_ACCOUNTS", "10"))     # reference: 16 acct x marketplace
SOFFICE = os.getenv("SOFFICE", r"C:\Program Files\LibreOffice\program\soffice.exe")


def log(msg):
    line = "%s  %s" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg)
    print(line, flush=True)
    try:
        with io.open(LOG, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except Exception:
        pass


def write_status(ok, msg, extra=None):
    st = dict(ok=ok, message=msg, when=datetime.now(timezone.utc).isoformat(timespec="seconds"),
              dry_run=DRY)
    if extra:
        st.update(extra)
    try:
        json.dump(st, io.open(STATUS, "w", encoding="utf-8"), indent=1)
    except Exception:
        pass


def die(msg):
    log("ABORT: " + msg)
    write_status(False, msg)
    sys.exit(2)


def last_good():
    """Row count from the last successful run, for the collapse guard."""
    try:
        st = json.load(io.open(STATUS, encoding="utf-8"))
        return int(st.get("listings") or 0) if st.get("ok") else 0
    except Exception:
        return 0


def month_end_before(today):
    """Last day of the previous calendar month."""
    first_of_this = today.replace(day=1)
    return first_of_this - timedelta(days=1)


def main():
    t0 = time.time()
    log("=" * 78)
    log("ESNM monthly refresh starting%s" % ("  [DRY RUN]" if DRY else ""))

    # ---------- anchor ----------
    if "--anchor" in sys.argv:
        anchor = date(*[int(x) for x in sys.argv[sys.argv.index("--anchor") + 1].split("-")])
    else:
        anchor = month_end_before(date.today())
    period = "%04d-%02d" % (anchor.year, anchor.month)
    log("anchor = %s (last day of the previous month) · period = %s" % (anchor, period))

    import build_esnm_d01 as B
    import render_esnm_dashboard as R
    B.set_anchor(anchor)
    R.B = B                                    # renderer reads B.ANCHOR / B.W* dynamically
    log("windows: 30d %s..%s · 90d %s..%s · LY30 %s..%s · LY90 %s..%s"
        % (B.W30_A, B.ANCHOR, B.W90_A, B.ANCHOR, B.LY30_A, B.LY_B, B.LY_A, B.LY_B))

    # ---------- pull, with retry (the fleet has seen transient VPN drops) ----------
    data = None
    for attempt in (1, 2, 3):
        try:
            data = B.fetch()
            break
        except Exception as e:
            log("  fetch attempt %d failed: %s" % (attempt, str(e).splitlines()[0]))
            if attempt == 3:
                die("all 3 fetch attempts failed: %s" % str(e).splitlines()[0])
            time.sleep(20 * attempt)

    rows = B.assemble(data)
    n = len(rows)
    accounts = len({r["account"] for r in rows})
    counts = {}
    for r in rows:
        counts[r["rule_no"]] = counts.get(r["rule_no"], 0) + 1
    crit = counts.get(1, 0)
    log("pulled %d listings · %d account x marketplace · %d Critical" % (n, accounts, crit))

    # ---------- GATES (all before any write) ----------
    prev = last_good()
    if n < MIN_LISTINGS:
        die("only %d listings (< floor %d) — looks like a broken pull, not a small month"
            % (n, MIN_LISTINGS))
    if accounts < MIN_ACCOUNTS:
        die("only %d account x marketplace combinations (< floor %d)" % (accounts, MIN_ACCOUNTS))
    if prev and n < prev * (1 - MAX_DROP):
        die("listing count collapsed %d -> %d (>%.0f%% drop vs last good run). A feed that "
            "silently half-empties clears an absolute floor, which is why this guard exists."
            % (prev, n, MAX_DROP * 100))
    if crit == 0:
        die("zero Critical listings — Rule 1 produced nothing, which has never happened; "
            "treat as a broken sales pull")
    if crit == n:
        die("every listing is Critical — the sales join returned nothing")
    log("gates passed (floor %d · accounts %d · collapse guard vs %s)"
        % (MIN_LISTINGS, MIN_ACCOUNTS, prev or "no prior run"))

    # ---------- build all three artefacts from THIS one snapshot ----------
    B.build(rows, data["cov"])
    R.main(rows, data["cov"])
    log("artefacts rebuilt from a single snapshot")

    # ---------- recalculate the workbook (openpyxl writes formulas with no cached values) ----
    xlsx = B.OUT_XLSX
    if os.path.isfile(SOFFICE):
        tmp = os.path.join(FINAL, "_rc")
        shutil.rmtree(tmp, ignore_errors=True)
        os.makedirs(tmp, exist_ok=True)
        rc = subprocess.call([SOFFICE, "--headless", "--norestore", "--convert-to",
                              "xlsx:Calc MS Excel 2007 XML", "--outdir", tmp, xlsx],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        out = os.path.join(tmp, os.path.basename(xlsx))
        if rc == 0 and os.path.isfile(out):
            shutil.copyfile(out, xlsx)
            log("workbook formulas recalculated")
        else:
            log("WARNING: LibreOffice recalc failed (rc=%s) — the xlsx formulas have no cached "
                "values, so pandas/openpyxl will read them as blank. HTML is unaffected." % rc)
        shutil.rmtree(tmp, ignore_errors=True)
    else:
        log("WARNING: LibreOffice not found at %s — workbook not recalculated" % SOFFICE)

    # ---------- publish ----------
    if DRY:
        log("DRY RUN — ph_task NOT touched")
        log("NOTE: a dry run still REBUILDS the on-disk artefacts. If you dry-ran with an anchor "
            "other than the one currently published, the files on disk now differ from ph_task. "
            "Re-run with the published anchor to resync, or run for real.")
    else:
        sys.path.insert(0, HERE)
        import publish_esnm_ph_task as P
        P.PERIOD = period                       # task_id carries the report month
        P.main_publish()
        log("published to ph_task for %s" % period)

    write_status(True, "ok", dict(listings=n, critical=crit, accounts=accounts,
                                  anchor=anchor.isoformat(), period=period,
                                  seconds=round(time.time() - t0, 1)))
    log("DONE in %.1fs — %d listings, %d Critical" % (time.time() - t0, n, crit))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        tb = traceback.format_exc()
        log("UNHANDLED:\n" + tb)
        write_status(False, "unhandled exception: " + tb.strip().splitlines()[-1])
        sys.exit(3)
