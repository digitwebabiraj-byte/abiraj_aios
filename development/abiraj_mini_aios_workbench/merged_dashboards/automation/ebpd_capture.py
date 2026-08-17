# -*- coding: utf-8 -*-
"""
Read-only capture of EBPD's FRESH data by running its own weekly runner with --no-publish
(so it pulls live + builds but publishes NOTHING), then dumping the in-memory ROWS (+ the
reporting-month label) to EBPD_OUT for the merge emitter. Never modifies the EBPD task; the
runner's incidental writes (ebpd_auto_dashboard.html / ebpd_status.txt) are restored by the
caller via git checkout.

  EBPD_RUNNER=<path to ebpd_weekly_run.py>  EBPD_OUT=<path to write>  python ebpd_capture.py
"""
import os, sys, json, runpy

RUNNER = os.environ["EBPD_RUNNER"]
OUT = os.environ["EBPD_OUT"]

# EBPD's runner keys off sys.argv for the no-publish gate; force it and run as __main__.
sys.argv = [RUNNER, "--no-publish"]
ns = runpy.run_path(RUNNER, run_name="__main__")   # executes the live pull + build, no publish

rows = ns.get("ROWS")
label = ns.get("REP_LABEL", "")
if not rows:
    sys.exit("EBPD capture: no ROWS produced")
json.dump({"rows": rows, "label": label}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
print("EBPD capture ok: %d rows | %s -> %s" % (len(rows), label, OUT))
