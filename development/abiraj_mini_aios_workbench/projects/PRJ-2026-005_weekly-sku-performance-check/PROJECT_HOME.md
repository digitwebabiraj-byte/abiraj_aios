# PROJECT_HOME — Weekly SKU Performance Check (Table 7)

## Project ID

PRJ-2026-005_weekly-sku-performance-check

## Project Name

Table 7 — Weekly SKU Performance Check | All Platforms UK (Amazon · eBay · B&Q)

## Purpose

Automate the recurring weekly **Table 7** report for Portfolio Holder **Thuwaraga**:
group all of her UK listings by resolved base SKU and show a rolling 7-day Completed-order
count per platform (Amazon / eBay / B&Q), flagging every listing with zero orders in the
window. Replaces the hand-maintained weekly spreadsheet with a governed, database-derived
report — one blue "ASIN detail" row per listing, one purple "SKU SUMMARY" row per SKU family —
where every figure ties to a real `schema.table.column`; unproven fields are parked, never
invented.

## Business Question

For each of Thuwaraga's UK listings across Amazon, eBay and B&Q — how many Completed orders
did it take in the last rolling 7 days, which listings sold nothing, and for each SKU family
how many of its ASINs are performing — answered from the database alone, run every Thursday
with the window computed dynamically, with no weekly manual re-keying?

Status: **CONFIRMED** from the approved Table 7 spec (sheet `PH-2026-07-THUW07 - Abiraj` in
`PHs Daily works - Dev_Automation.xlsx`) and `HANDOFF_weekly_sku_performance_check.md`.

## Owner and Reviewers

- Owner / Developer: Abiraj
- End user (Portfolio Holder): Thuwaraga (sheet spelling "Thuwaraha"; **DB spelling `thuwaraga`**)
- Technical Reviewer: Sajeesan
- Queryability Reviewer: Tamil Selvan
- Coordinator: Varmen
- Business Validator: to be assigned per task type (assignment pending)

## Original Requirement

- **T7 (Task 7 / Table 7, project code `PH-2026-07-THUW07`)** — Weekly SKU Performance Check.
  - **D01 (2026-07-09, Phase-01 — Reporting & Presentation):** governed dataset rebuild query
    (`generate_dataset.sql`) + Portfolio-Holder-facing interactive **HTML dashboard** and a
    template-matching **.xlsx**, for the first live window **02-Jul-2026 → 08-Jul-2026**.
    Reconciled to the live DB; zero-order listings flagged; data-quality risks surfaced.

## Approved Scope

- Maintain this project folder (`projects/PRJ-2026-005_weekly-sku-performance-check/`) only.
- **READ-ONLY** inspection of the production PostgreSQL DB `order_management_copy` via the
  Postgres MCP connector, for discovery, the dataset pull and evidence.
- COPY-only import of the delivery handoff from `C:\Users\digit\Downloads\` (originals preserved).
- Generate the dataset query + the HTML/xlsx renderers and their outputs. **No DB object created,
  dropped or altered** (this report needs no reporting view — it is a per-run extract).

## Prohibited Scope

- No `INSERT`/`UPDATE`/`DELETE`, no DDL, no schema change anywhere in the DB.
- Do not invent orders, SKU→SKU mappings, product names or account attributions not present in
  the database. Unclear fields are flagged, not decided.
- Do not modify anything outside this project folder without written approval.
- Do not commit or push without explicit instruction.

## Systems and Sources

- Database: **PostgreSQL `order_management_copy`** (production), read-only via the Postgres MCP.
  (Connector GUIDs rotate per session — rely on the DB name, not the id.)
- Key source objects (read-only):
  - `public.order_transaction` — orders + listing universe (one row per line item). Filter
    `LOWER(user_name)='thuwaraga'`, `market_place='UK'`, `source_name IN ('AMAZON','EBAY','B&Q')`.
  - `public.listing_data` — SKU/ASIN registry; resolves base SKU (`mapped_sku` else `sku`) and
    product `title`. Filter `wrong_sku=0`.
- Spec / acceptance source: sheet `PH-2026-07-THUW07 - Abiraj` (Table 7 layout + colour legend +
  sample rows) and `HANDOFF_weekly_sku_performance_check.md`.

## Imported / Generated Assets

Under Task `T7_weekly-sku-performance-check` (COPY-only import; originals in Downloads preserved):

- `evidence/source_documents/T7_weekly-sku-performance-check/HANDOFF.md` — the approved handoff.
- `sql/T7_weekly-sku-performance-check/generate_dataset.sql` — canonical read-only rebuild query.
- `evidence/final_outputs/T7_weekly-sku-performance-check/`:
  - `data.json` — governed pull (2,114 listing rows + 628 product names + run metadata).
  - `build_html.py` → `Table7_Weekly_SKU_Performance_Thuwaraga.html` (interactive dashboard).
  - `build_report.py` → `Table7_Weekly_SKU_Performance_Thuwaraga.xlsx` (template-matching sheet).
- `validation/T7_weekly-sku-performance-check/2026-07-09_validation.md` — reconciliation evidence.

## Source-of-Truth Locations

- **Dashboard (current key deliverable):**
  `evidence/final_outputs/T7_weekly-sku-performance-check/Table7_Weekly_SKU_Performance_Thuwaraga.html`
  (regenerate via `build_html.py`; data spine `data.json`; rebuild query `generate_dataset.sql`).
- **Spreadsheet:** `…/Table7_Weekly_SKU_Performance_Thuwaraga.xlsx` (regenerate via `build_report.py`).
- **Locked rules / functional detail:** `SYSTEM_REFERENCE.md`.
- **Approved handoff:** `evidence/source_documents/T7_weekly-sku-performance-check/HANDOFF.md`.

## Run Snapshot (2026-07-09, window 02-Jul → 08-Jul-2026, **as of 14:17 Asia/Colombo**)

- **218 product families** (grouping = base SKU + its pack-size variants merged; owner-confirmed
  2026-07-09) · 2,140 listings (18 `amzn.gr.*` group-id pseudo-SKUs excluded, all zero-order).
- **110 listings performing** (≥1 Completed order) · 2,030 at zero.
- **170 orders total** — Amazon 122 · eBay 27 · B&Q 21.
- 43 active families · 175 zero-order families · 138 families merge >1 SKU (tagged `+N SKUs`).
- **Live-DB note:** the source DB keeps ingesting; an earlier 12:00 read showed 150 orders, 14:17
  showed 170. Marketplace orders settle for ~1–2 days after a window closes, so each run carries an
  `as of` timestamp (dashboard header · xlsx subtitle · `data.json.meta.snapshot_at`).

## Known Risks

- **SKU-family grouping is derived, not sourced.** The template groups pack-size variants under one
  product (e.g. `LDMG80B224` + `…2PK`/`…3PK`/`…APK`), but **no field in the DB encodes that
  relationship** (`mapped_sku` is empty/dirty). Owner confirmed (2026-07-09) to **merge by product**:
  strip a recognised pack suffix (`\d+PK`/`APK`/`PCK\d+`) **only when the stripped base is itself a
  real SKU** in the universe — anchored + reversible, no relationship invented. Families that roll
  up >1 SKU are tagged `+N SKUs` (138 of 218) for reviewer verification. `mapped_sku` is **not** used
  for grouping (it reassigns some listings cross-family — e.g. a G95 bulb → a C35 candle base).
- **Listing sprawl inflates "not performing".** 95% of listings show 0 orders because each SKU
  carries many idle cross-listings (relistings, multi-account, retired ASINs). Literal "flag every
  0" is faithful to the spec but noisy; the dashboard defaults to **Active families** and offers
  All / Zero-order / Merged filters so the red band isn't misread as 2,000 faults.
- **`amzn.gr.*` pseudo-SKUs** (18) are Amazon internal group IDs, not products; excluded by the
  renderer (all zero-order). Kept visible in SQL for auditability.
- **Product name quality:** every row resolves a name, but some `listing_data.title` values are
  variant option labels ("Ten", "Paquet de 6") rather than full titles; category fallback fills
  blanks. Acceptable; noted.
- **Scheduling not yet wired** — window is currently set in `generate_dataset.sql`; the Thursday
  trigger + dynamic `CURRENT_DATE` window is an open item (see TASK_REGISTER).

## Live Publish

The finished dashboard is published as **one governed row** in the shared team output store
`tech_team_outputs.ph_task` (DB `order_management_copy`) — **row id 135**:
`project_code=WSPC` · `task_id=WSPC_thuwaraga_SKU_Performance_Dashboard-V1` · `task_name=T7 · Weekly
SKU Performance Check — Thuwaraga UK (Amazon · eBay · B&Q)` · `team=Development` · `developer=Abiraj`
· `assigned_user=thuwaraga` · `assigned_user_team=ph_priors` · `version_status=released`. Written via
guarded single-row `INSERT`/`UPDATE` (owner-authorised); no other row touched, no application/`public`
data changed. The DB row holds the same HTML as `Table7_Weekly_SKU_Performance_Thuwaraga.html`.

## Status

**COMPLETE — VALIDATED & CLOSED (2026-07-09).** Dataset query + HTML dashboard + xlsx built for the
02-Jul→08-Jul-2026 window, reconciled to the live DB via an independent direct order-count
(snapshot 14:17: 110 performing / 170 orders / 122-27-21 / 218 families), and published live to
`tech_team_outputs.ph_task` (row 135). The SKU-family grouping (merge-by-product) was owner-confirmed;
data-quality items were flagged, not silently fixed. **Read, validated and signed off by Thuwaraga
(end user) and Satheewaran on 2026-07-09.** No carried-open items for REQ-07-D01.

## One Next Action

**None for REQ-07-D01 — delivered, live and closed.** Optional *future* requirement (separable,
e.g. REQ-07-D02): wire a Thursday scheduled run with a dynamic `CURRENT_DATE` window to refresh
row 135 automatically each week, and parameterise for multi-PH coverage.
