# -*- coding: utf-8 -*-
"""
REQ-16-D01 — build ALL THREE artefacts from ONE live snapshot.

**Always use this instead of running the builder and the renderer separately.**

Why it exists: `build_esnm_d01.py` and `render_esnm_dashboard.py` each called `fetch()`
independently. Because the anchor is a partial day and orders keep arriving, two runs minutes
apart return different data — the workbook ended up with 11,156 listings while the dashboard had
11,176, and the same listing could carry a different Action in each. The verification harness
caught it (`xlsx 11156 != dashboard 11176`). Two artefacts of one deliverable disagreeing is worse
than either being slightly stale.

This fetches once and hands the same rows to both renderers, so they cannot drift.

    python build_esnm_all.py

Note it does NOT recalculate the workbook's formulas — openpyxl writes formulas without cached
values. Run the LibreOffice recalc afterwards, or the xlsx will read as empty to pandas/openpyxl.
"""
import os, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import build_esnm_d01 as B
import render_esnm_dashboard as R


def main():
    print("=== ONE fetch, three artefacts ===", flush=True)
    data = B.fetch()
    rows = B.assemble(data)
    print("assembled rows: %d" % len(rows), flush=True)

    counts = {}
    for r in rows:
        counts[r["rule_no"]] = counts.get(r["rule_no"], 0) + 1
    print("rule counts:", json.dumps({str(k): v for k, v in sorted(counts.items())}), flush=True)

    xlsx = B.build(rows, data["cov"])
    print("workbook  :", xlsx, flush=True)

    R.main(rows, data["cov"])

    print("\nBoth artefacts share one snapshot of %d rows." % len(rows))
    print("NEXT: recalculate the workbook formulas, then re-run")
    print("      validation/REQ-16_ebay-slow-no-moving-products/verify_esnm_d01.py")


if __name__ == "__main__":
    main()
