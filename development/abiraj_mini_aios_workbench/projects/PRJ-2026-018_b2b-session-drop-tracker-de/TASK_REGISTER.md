# TASK REGISTER — PRJ-2026-018 (`bsdt`)

| Deliverable | What | Status | Evidence |
|---|---|---|---|
| REQ-21-D01 | B2B Session Drop Tracker — Amazon.de, per-ASIN two-window B2B sessions/page-views/orders + Buy Box % + Session Change + Tier/Status/Action | ✅ **BUILT + VERIFIED 2026-07-31** (xlsx + interactive dashboard; engine 0 mismatches; publish held for audience/IDs) | `evidence/final_outputs/REQ-21_b2b-session-drop-tracker-de/` |
| REQ-21-D02 | Scheduled refresh (optional, like the other trackers) | NOT STARTED | — |

## Timeline
- **2026-07-31** — Onboarded from `B2B_Session_Drop_Tracker_DE.xlsx` (owner-delivered, Downloads).
  Read all 3 tabs (Objective & Guide, Thresholds, Tracker/528 rows). **Proved DB-reproducible:**
  B2B metrics live in `business_reports.amz_traffic_by_asin`; Germany = `market_place 10`,
  `sub_source 8`; reference ASIN `B0DLWRP73C` reconciles to the unit (DB 19 = sheet 15+4).
  Source imported COPY-only with SHA-256. No build, no publish, no commit.

## Locked understanding
- Tier by `MAX(prev, current)` B2B Sessions vs editable boundaries (T2 ≥5, T3 ≥10).
- B2B-only columns (never blended B2B+B2C). Include an ASIN only if it has B2B traffic in ≥1 window.
- Session Change / Units / Buy Box % are context — they never change tier or action.

## Open / next (blocks BUILD)
1. **Publish audience** — end user = **Jensika** (`staff.users` id 99, Active, Nelliady). `ph_task` audience/team still to confirm.
2. **Exact 30-day window anchor** — reference ASIN's B2B data ends 2026-04-14, so windows are NOT
   "last 30 days from today"; confirm the owner's export "as of" date.
3. **sub_source scope** — confirm `sub_source = 8` is the only .de account in scope.
4. **Confirm IDs** — `REQ-21` / code `bsdt` provisional.
5. **Grain** — confirm child-ASIN (no parent rollup).
