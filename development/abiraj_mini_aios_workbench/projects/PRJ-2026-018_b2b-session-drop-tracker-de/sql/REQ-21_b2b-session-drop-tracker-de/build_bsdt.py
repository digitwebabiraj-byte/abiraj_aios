#!/usr/bin/env python3
"""
REQ-21-D01 — B2B Session Drop Tracker (Amazon.de / Germany) — dataset builder.

System of record = the owner-supplied Amazon.de Seller Central Business Report export,
delivered as `B2B_Session_Drop_Tracker_DE.xlsx`. This script reads that export, RE-DERIVES the
engine columns (Session Change, Tier, Status, Action) from the editable thresholds so nothing is
trusted blindly, verifies they match the source, and emits a governed bsdt_data.json.

Read-only on the source; writes only bsdt_data.json.
"""
import json, sys, hashlib
from pathlib import Path
import openpyxl

HERE = Path(__file__).resolve().parent
PROJ = HERE.parent.parent
SRC  = PROJ / "evidence/source_documents/REQ-21_b2b-session-drop-tracker-de/B2B_Session_Drop_Tracker_DE.xlsx"
OUT  = HERE / "bsdt_data.json"

# --- Confirmed task parameters (owner-confirmed 2026-07-31) ---
META = {
    "project": "B2B Session Drop Tracker — Germany (Amazon.de)",
    "project_code": "bsdt",
    "requirement_id": "REQ-21",
    "deliverable_id": "REQ-21-D01",
    "end_user": "Jensika (staff.users id 99)",
    "scope": "Amazon.de (Germany) account only",
    "source_of_record": "Amazon.de Seller Central Business Report export (Detail Page Sales and Traffic by Child Item), B2B columns",
    "current_window": {"start": "2026-06-16", "end": "2026-07-15", "label": "16 Jun 2026 – 15 Jul 2026"},
    "previous_window": {"start": "2026-05-17", "end": "2026-06-15", "label": "17 May 2026 – 15 Jun 2026"},
    "thresholds": {"tier2_min_sessions": 5, "tier3_min_sessions": 10},
    "engine_note": "Tier = MAX(prev,current) B2B Sessions vs thresholds. Session Change, Units Orders and Buy Box % are context only; they never change Tier/Status/Action.",
}

def tier_of(mx, t2, t3):
    if mx < t2: return "Tier 1 - Low"
    if mx < t3: return "Tier 2 - Moderate"
    return "Tier 3 - High"

def num(v):
    return 0 if v is None else (int(v) if float(v).is_integer() else float(v))

def main():
    t2 = META["thresholds"]["tier2_min_sessions"]
    t3 = META["thresholds"]["tier3_min_sessions"]
    wb = openpyxl.load_workbook(SRC, data_only=True)
    ws = wb["Tracker"]
    raw = [r for r in ws.iter_rows(values_only=True) if r[0] and r[0] != "ASIN"]

    # canonical Status/Action text per Tier, taken verbatim from the source
    status_txt, action_txt = {}, {}
    for r in raw:
        status_txt.setdefault(r[9], r[10]); action_txt.setdefault(r[9], r[11])

    rows, mism = [], {"session_change": 0, "tier": 0, "status": 0, "action": 0}
    for r in raw:
        prevS, currS = num(r[1]), num(r[4])
        exp_sc   = currS - prevS
        exp_tier = tier_of(max(prevS, currS), t2, t3)
        if r[8] is not None and num(r[8]) != exp_sc: mism["session_change"] += 1
        if r[9] != exp_tier:                          mism["tier"] += 1
        if r[10] != status_txt.get(r[9]):             mism["status"] += 1
        if r[11] != action_txt.get(r[9]):             mism["action"] += 1
        rows.append({
            "asin": r[0],
            "prev_sessions": prevS, "prev_page_views": num(r[2]), "prev_orders": num(r[3]),
            "curr_sessions": currS, "curr_page_views": num(r[5]), "curr_orders": num(r[6]),
            "buy_box_pct": None if r[7] is None else round(float(r[7]) * 100, 2),
            "session_change": exp_sc,
            "tier": exp_tier, "status": status_txt.get(exp_tier), "action": action_txt.get(exp_tier),
        })

    if any(mism.values()):
        print("ENGINE VERIFICATION FAILED:", mism); sys.exit(1)

    from collections import Counter
    dist = dict(Counter(x["tier"] for x in rows))
    payload = {
        "meta": META,
        "generated_from_sha256": hashlib.sha256(SRC.read_bytes()).hexdigest(),
        "row_count": len(rows),
        "tier_distribution": dist,
        "tier_status": status_txt,
        "tier_action": action_txt,
        "rows": rows,
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"OK — {len(rows)} rows, engine verified 0 mismatches.")
    print("Tier distribution:", dist)
    print("Wrote", OUT)

if __name__ == "__main__":
    main()
