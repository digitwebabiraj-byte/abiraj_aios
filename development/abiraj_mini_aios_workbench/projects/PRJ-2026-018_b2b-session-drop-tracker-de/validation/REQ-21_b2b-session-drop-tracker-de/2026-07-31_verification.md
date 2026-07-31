# Verification Record — REQ-21-D01 (B2B Session Drop Tracker · Amazon.de)

Date: 2026-07-31 · Read-only against the source; independent re-derivation.

## 1. Engine re-derivation (source Excel)
The tier/action engine was re-implemented independently and checked against the source's own
columns for every row.

| Check | Result |
|---|---|
| Rows tested | 526 |
| Session Change (Current − Prev sessions) mismatches | **0** |
| Tier (MAX(prev,current) vs T2≥5 / T3≥10) mismatches | **0** |
| Status consistency (one per tier) breaks | **0** |
| Action consistency (one per tier) breaks | **0** |
| Tier distribution | Tier 1 Low **506** · Tier 2 Mod **16** · Tier 3 High **4** |

## 2. Cross-artefact reconciliation
| Pair | Result |
|---|---|
| Source Excel ↔ governed `bsdt_data.json` | 526/526 rows, **0 mismatches** |
| Built xlsx literal values ↔ JSON (sessions/pv/orders/status/action) | **0 mismatches** |
| xlsx Tier formulas simulated (Thresholds B4=5, B5=10) vs known tiers | **0 mismatches** |
| Dashboard embedded rows ↔ JSON | **identical** |

## 3. Defect found & fixed
- The xlsx Tier formula initially referenced `Thresholds!$B$2/$B$3` (the header and Tier-1 label
  cells) instead of the editable threshold values in `B4` (Tier 2 = 5) / `B5` (Tier 3 = 10). In
  Excel that would compare a number against text and collapse every row to Tier 1. Corrected to
  `$B$4`/`$B$5`; re-simulated → 0 mismatches. Thresholds-sheet note corrected to match.

## 4. Data-source verdict (why the DB is not used)
Full 526-ASIN completeness test against `business_reports.amz_traffic_by_asin`:
- Germany scope: 359 (68%) sheet ASINs have **zero** DB B2B; 406 (77%) exceed DB all-time → ~23%
  reproducible.
- All marketplaces + all-time (most generous): still 252 (48%) zero, 295 (56%) impossible.
- May 2026 entirely missing from the .de feed; 51 ASINs absent from the table.
⇒ The DB cannot reproduce the report; the Amazon Seller Central export is the system of record
(owner-confirmed 2026-07-31). Detail: `evidence/DATA_SOURCE_ANALYSIS.md`.

## Verdict
REQ-21-D01 is internally consistent and faithful to the owner-supplied source — **GREEN (technical,
self-checked)**. Reviewer + business sign-off and `ph_task` publish remain pending (audience/IDs).

## 5. Dashboard publish-readiness (2026-07-31, addendum)
- **No-JS static fallback added:** all 526 rows are pre-rendered server-side into the HTML `<tbody>`
  (default-sorted biggest-drop-first), so the table renders even where the `ph_task` viewer does not
  run JS (the EBPD/EPPR lesson). JS enhances with live filter/sort when available. Verified: 526
  static `<tr>` present; first row = `B0DLWRP73C` (Δ −11, the largest drop).
- **Filters:** ASIN search · Tier · Trend · Buy Box · B2B Orders · Reset (with active-filter count) ·
  Export CSV — all combine (AND); CSV respects the active view.
- **Fonts embedded** (Inter ×5 + JetBrains Mono ×2 for ASINs) — self-contained, offline-identical.
- **Theme:** Emerald + Charcoal; Tier badges kept red/amber/slate (severity); Tier-3 rows carry a
  faint red left accent.
