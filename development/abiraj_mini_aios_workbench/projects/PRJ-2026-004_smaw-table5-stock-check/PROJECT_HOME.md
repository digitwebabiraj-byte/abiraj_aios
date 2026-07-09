# PROJECT_HOME — SMAW Table 5 Weekly Stock Check

## Project ID

PRJ-2026-004_smaw-table5-stock-check

## Project Name

SMAW — Stock Management Across All ASINs & Warehouses (Table 5 Weekly Stock Check)

## Purpose

Provide one canonical AIOS project home for Abiraj's **Table 5 Weekly Stock Check** work for
Portfolio Holder **Thuwaraga**: replace the hand-maintained weekly stock spreadsheet (Amazon
FBM + UK warehouse + incoming supplier shipments) with a governed single-source stock truth —
one row per (ASIN, account) that rolls every listing SKU/ASIN back to one master SKU, computes
Sales Velocity / Days-of-Stock-Remaining / Stock Status, and renders it as a Portfolio-Holder-
facing dashboard. Every output column is tied to a real `schema.table.column`; unproven fields
are parked, never invented.

## Business Question

For each of Thuwaraga's ASINs / listing SKUs — what is the master SKU, how much real stock sits
in the UK warehouse, what is the last-90-day sales velocity, how many days of stock remain, what
is incoming from suppliers, and what is the resulting Stock Status (Healthy / Going Out / No
Stock) — answered from the database alone, with no weekly manual re-keying and no listing↔stock
guesswork?

Status: **CONFIRMED** (from the approved Table 5 spec `table_5-abiraj.xlsx` — HIGH PRIORITY,
weekly every Monday).

## Owner and Reviewers

- Owner: Abiraj
- End user (Portfolio Holder): Thuwaraga
- Technical Reviewer: Sajeesan
- Queryability Reviewer: Tamil Selvan
- Business Validator: To be assigned per task type (assignment pending)

## Original Requirement

- **REQ-06** — Table 5 Weekly Stock Check, first governed view. Deliverables:
  - **D01 (2026-07-08, Phase-01 — Reporting & Data Model):** governed read-only view
    `v_table5_weekly_stock_check` + column→source evidence map + duplicate-risk scan.
    Row colouring declared **out of SQL scope**.
  - **D02 (2026-07-09, Phase-02 — Reporting & Presentation):** Portfolio-Holder-facing
    interactive **HTML dashboard** rendering the Table 5 output (delivers the Peacock/Yellow/Red
    colour bands D01 left to the renderer) + scopes the full-portfolio (all-ASIN) expansion.
  - **D03 (2026-07-09, Phase-03 — Full-Portfolio Coverage):** the all-ASIN build — universe =
    every Amazon-UK ASIN with a live FBM listing OR a 90-day sale (listings ∪ `analytics.ph_segment`
    ∪ sales), a strict superset of the sellers plus all idle stock. **733 ASINs**; all-ASIN HTML
    dashboard that splits the zero-stock reds into real **Stockouts (9)** vs **Inactive listings (119)**.

## Approved Scope

- Maintain this project folder and its subfolders only.
- **READ-ONLY** inspection of the production PostgreSQL DB `order_management_copy` via the
  "Postgresql" MCP connector, for discovery, verification and evidence.
- COPY-only import of the delivery artifacts from `C:\Users\digit\Downloads\` (originals
  preserved).
- Create the reporting view (D01, in an approved reporting schema) and the HTML dashboard +
  generator (D02) — no other DB object created, dropped or altered.

## Prohibited Scope

- No `INSERT`/`UPDATE`/`DELETE`, no DDL against `public` / `supplier` / `staging_ai` live tables,
  no schema change.
- Do not invent stock numbers, FBA figures, container dates, or SKU→SKU mappings not present in
  the database. Unclear fields are flagged, not decided.
- Do not modify anything outside this project folder without written approval.
- Do not commit or push without explicit instruction.

## Systems and Sources

- Database: **PostgreSQL `order_management_copy`** (production), read-only via the "Postgresql"
  MCP. A parallel `development` DB carries the same tables. (Connector GUIDs rotate per session —
  rely on the DB name, not the id.)
- Key source objects (read-only):
  `public.location_wise_inv_stock` (UK stock truth — matches the live inventory UI; feed
  `updated_at = 2026-05-04`) · `public.order_transaction` (velocity + sales universe) ·
  `public.listing_data` (listing SKU + `mapped_sku` + FBM qty) · `supplier.suppliers` /
  `supplier.orders` / `supplier.order_items` / `supplier.final_containers` (incoming PO/container).
- Spec / acceptance source: `table_5-abiraj.xlsx` (Table 5 layout + colour spec + sample rows).

## Imported Assets

Imported 2026-07-09 under Task `REQ-06_table5-weekly-stock-check` (COPY-only; originals in
`C:\Users\digit\Downloads\` preserved):

- `evidence/source_documents/REQ-06_table5-weekly-stock-check/HANDOFF.md` — locked decisions +
  open task + validation steps.
- `sql/REQ-06_table5-weekly-stock-check/generate_dataset.sql` — the dataset-rebuild query.
- `evidence/final_outputs/REQ-06_table5-weekly-stock-check/`:
  - **Sellers-only (D01/D02, 240 rows):** `dataset.py` · `build_report.py` (Excel) ·
    `build_html.py` → `Table5_Weekly_Stock_Check_Thuwaraga.html`.
  - **Full-portfolio (D03, 733 ASINs):** `data_all.json` (raw pull) · `build_all.py` (plain
    HTML + Excel) · `build_all_html.py` → `Table5_Weekly_Stock_Check_Thuwaraga_ALL.html`
    (polished dashboard) · `Table5_Weekly_Stock_Check_Thuwaraga_ALL.xlsx`.
- `sql/.../generate_dataset_all_asins.sql` — all-ASIN rebuild query (D03).
- `evidence/source_documents/.../RUN_IN_CLAUDE_CODE.md` — D03 run instructions / handoff.

## Source-of-Truth Locations

- **D03 full-portfolio dashboard (current key deliverable, 733 ASINs):**
  `evidence/final_outputs/REQ-06_table5-weekly-stock-check/Table5_Weekly_Stock_Check_Thuwaraga_ALL.html`
  (regenerate via `build_all_html.py`; data spine `data_all.json`; rebuild query
  `sql/.../generate_dataset_all_asins.sql`).
- **D02 sellers-only dashboard (240 rows):**
  `evidence/final_outputs/REQ-06_table5-weekly-stock-check/Table5_Weekly_Stock_Check_Thuwaraga.html`
  (regenerate via `build_html.py`; data spine `dataset.py`; rebuild query `generate_dataset.sql`).
- **Locked decisions / handoff:**
  `evidence/source_documents/REQ-06_table5-weekly-stock-check/HANDOFF.md`.
- **Requirement docs (referenced, live outside this project):**
  `DigitWeb_Works_Abiraj/08_07_2026/2026-07-08_abiraj_REQ-smaw_REQ-06-D01.md` ·
  `DigitWeb_Works_Abiraj/09_07_2026/2026-07-09_abiraj_REQ-smaw_REQ-06-D02.md`.
- **Project-level:** `SYSTEM_REFERENCE.md`.

## Known Risks

- **Legacy→canonical SKU alias gap:** sales booked under a drained legacy SKU while stock sits on
  the canonical variant, e.g. `LDMA60E274` reads 0 while `LDMA60E274WW` holds 3,233. No SKU→SKU
  master-mapping table exists in `order_management_copy` beyond `listing_data.mapped_sku` (NULL
  for these). 4 rows auto-flagged `LEGACY?` (B0DG25H3RQ, B0DGL8XMR7, B0DG2BN5YP, B0DGKR9FSM).
  **Decision: flag, do not auto-correct.**
- **Sales-only coverage — RESOLVED in D03.** The all-ASIN build now covers the full portfolio
  (733 ASINs: listings ∪ `analytics.ph_segment` ∪ 90-day sales, a strict superset of the 240
  sellers — 0 dropped). Note the SQL marks every 0-stock row "No Stock / Critical" (128 rows);
  the D03 dashboard splits these into **9 real Stockouts** (sold + 0 stock → reorder) vs **119
  Inactive listings** (no stock, no sales → dead) so the red band isn't misread. Labelling split
  awaiting Thuwaraga confirmation.
- **4 UNPROVEN D01 fields:** Amazon FBA on-hand source · container ETA date · W1/W2/W3 warehouse
  mapping · authoritative "Last Stock Checked Date".
- **Duplicate-truth:** `tech_team_outputs.ph_task` already holds `PSLD_thuwaraga_stock_Dashboard-V1`
  (project PSLD, dev Sarujanan, Released) — this render must complement, not duplicate it.
- Inventory feed frozen at `2026-05-04`; if a fresher feed exists, repoint the `inv` CTE and
  re-reconcile.

## Status

**DELIVERED & LIVE (2026-07-09).** D01 (governed report), D02 (sellers-only dashboard) and D03
(full-portfolio all-ASIN dashboard, **756 ASINs**) are complete, reconciled 0-mismatch to the live
DB, and **published** to `tech_team_outputs.ph_task` (id **122** V1=733 · id **137** V2=756, FBM-fixed,
both `released`). The Amazon-FBM display was corrected to match the live system (`wrong_sku` listings
now read their real qty, display-only). Remaining are confirmations, not build work: reviewer sign-off
(Tamil Selvan · Sajeesan) and Thuwaraga's nod on the Stockout/Inactive labelling.

## One Next Action

**Route the published V2 dashboard (`ph_task` id 137) for reviewer sign-off** (Tamil Selvan ·
Sajeesan) and Thuwaraga confirmation. (Standing, out of scope: obtain the legacy→canonical mapping
source to retire the last `LEGACY?` flags.)
