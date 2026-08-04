# TASK REGISTER — PRJ-2026-018 (`bsdt`)

| Deliverable | What | Status | Evidence |
|---|---|---|---|
| REQ-21-D01 | B2B Session Drop Tracker — Amazon.de, per-ASIN two-window B2B sessions/page-views/orders + Buy Box % + Session Change + Tier/Status/Action | ✅ **BUILT · VERIFIED · PUBLISHED 2026-07-31** (xlsx + dashboard; engine 0 mismatches; live on `ph_task` **id 669**, `assigned_user=jensika`, `assigned_user_team=ah_priors`, md5-verified) — business sign-off pending | `evidence/final_outputs/REQ-21_b2b-session-drop-tracker-de/` · `sql/REQ-21_.../publish_bsdt_ph_task.py` |
| REQ-21-D02 | Scheduled refresh (optional; needs a fresh 2-window export each cycle — the DB can't feed it) | NOT STARTED | — |

## Timeline
- **2026-07-31** — Onboarded from `B2B_Session_Drop_Tracker_DE.xlsx` (owner-delivered). Read all 3 tabs
  (Objective & Guide, Thresholds, Tracker/526 rows); source imported COPY-only + SHA-256.
- **2026-07-31** — 🔴 **Proved the DB does NOT reproduce the sheet.** B2B columns exist in
  `business_reports.amz_traffic_by_asin` (Germany `market_place 10`, `sub_source 8`) and one ASIN
  reconciled exactly, but a full 526-ASIN completeness test showed the DB holds only ~23% (Germany)
  of the sheet (May 2026 missing, ~half the ASINs absent). **Re-confirmed on the live DB** (host
  169.58.91.229): the two windows have only 2/30 (prev) + 5/30 (curr) days present.
- **2026-07-31** — Owner confirmed: source = **Amazon.de Seller Central Business Report export**
  (system of record); scope = **Amazon.de (Germany) account only**; windows **Current 2026-06-16→
  2026-07-15**, **Previous 2026-05-17→2026-06-15**; end user **Jensika** (`staff.users` id 99).
- **2026-07-31** — Built REQ-21-D01 **FRRC-style** from the export (engine re-derived, 0 mismatches;
  cross-artefact reconciled). Committed to `main` (`f5b3b51`).
- **2026-07-31** — **Published** to `tech_team_outputs.ph_task` **id 669** (`order_management_copy`
  warehouse) via guarded `temp_user` publisher (dry-run first, SELECT-then-INSERT, read-back md5
  verified), routed to **jensika** / **ah_priors**.

## Locked understanding
- Source of record = the Amazon.de Seller Central Business Report export (NOT the DB).
- Tier by `MAX(prev, current)` B2B Sessions vs editable boundaries (T2 ≥5, T3 ≥10).
- B2B-only columns (never blended B2B+B2C). Include an ASIN only if it has B2B traffic in ≥1 window.
- Session Change / Units / Buy Box % are context — they never change tier or action.

## Open / next
1. ✅ **Publish audience RESOLVED** — Jensika, `assigned_user_team=ah_priors`, live on `ph_task` id 669.
2. **Business sign-off** — Jensika to confirm the report.
3. **Confirm IDs** — `REQ-21` / code `bsdt` provisional (cosmetic).
4. **Optional REQ-21-D02** — scheduled refresh (needs a fresh export per cycle).
5. **Data-engineering (outside this report)** — the incomplete Amazon.de B2B sync (May 2026 missing;
   only ~10 days May–Jul) to raise with Sajeesan.
