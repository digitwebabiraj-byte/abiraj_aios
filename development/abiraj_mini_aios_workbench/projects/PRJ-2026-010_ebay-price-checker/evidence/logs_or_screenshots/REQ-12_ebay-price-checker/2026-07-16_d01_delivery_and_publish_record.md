# REQ-12-D01 — delivery + publish record (2026-07-16)

## What was delivered
A populated, read-only eBay price-checker report over **126,070 live eBay UK & DE listings** across
Thinesh's 13 accounts, in three artifacts (all in `evidence/final_outputs/REQ-12_.../`):
1. **`..._price-checker_UI.xlsx`** — one sheet, the source sheet's **exact 13 columns**, values not
   formulas, 126,070 rows. Reconciled 8/8 to the DB (see validation).
2. **`..._price-checker_dashboard.html`** — self-contained full-screen dashboard, all 126,070 rows
   virtualised, KPIs + status donut + 13-account chart + live filters/sort/search. Verified in-browser.
3. **`..._decision-sheet-thinesh.md`** — the Q1–Q8 decision sheet (now answered).

Build scripts registered alongside: `build_price_checker_xlsx.py`, `build_dashboard_html.py`.

## Results (all 126,070 rows)
| target_source | rows | | Status | rows |
|---|---|---|---|---|
| AMAZON | 47,982¹ | | ✅ Priced OK | 21,138 |
| WEBSITE_FALLBACK | 33,242¹ | | 🔴 Too high | 40,261 |
| NONE → DATA MISSING | 42,663 | | 🔴 Too low | 22,008 |
| | | | DATA MISSING — NO COMPARATOR | 21,048 |
| | | | DATA MISSING — BUNDLE | 21,615 |

¹ target_source counts are pre-account-filter (130,336-row basis); Status counts are the delivered
126,070. DATA MISSING = 42,663 either way. The 42,663 split: **21,048 eBay-only products** (no comparator)
+ **21,615 bundles** (components not all priced). Cross-checked: of ~6,800 distinct plain missing SKUs,
~84% are priced **nowhere** in either database (genuinely eBay-only); ~16% exist only outside Thinesh's
chosen Amazon account (recoverable by widening Q3). Germany misses at ~2× the UK rate because the DE
Amazon/website catalogues are ~half the UK size.

## Published to `tech_team_outputs.ph_task`
- **Target DB:** `order_management_copy` (host 10.8.0.3 internal / 149.28.134.54:5435 external — same
  instance), the team output registry. **NOT** the ledsone data source.
- **Method:** guarded single-row INSERT as `temp_user` (psycopg2), matching the sample script pattern —
  dry-run + rollback first (rowcount 1), then a duplicate-guarded INSERT + commit. Live has **no UNIQUE on
  `task_id`**, so the guard is manual (re-checked `task_id` + `project_code='epc'` inside the committing
  transaction). The dry-run consumed identity id 263 (sequences don't roll back); the committed row is
  **id 264**.
- **Row (id 264):** `project_code=epc` · `task_id=epc_Thinesh_ebay_price_checker-V1` ·
  `assigned_user=Thinesh` · `assigned_user_team=ebay_priors` · `team=Development` · `developer=Abiraj` ·
  `phase_level=1` · `version_level=1` · `version_status=released` · `html_content` = 17 MB dashboard.
- Verified independently via the Postgres MCP: exactly **one** `epc` row; the first attempt failed at
  `connect` ("too many clients"/"slots reserved for superusers") and wrote nothing.
- `description` was shortened in-place on 2026-07-16 (289 chars) via a guarded UPDATE, keeping the
  "⚠ Shipping-blind — rank, don't reprice; not yet signed off" flag.
- ⚠ 17 MB exceeds the table's historical max (14 MB); avg row is 370 kB. If the ph_task viewer app
  struggles, publish a lighter summary build via an in-place `UPDATE` (version_level bump).

## What this delivery does NOT settle (read before treating it as "the system")
- **Shipping-blind** — Status compares item price only; the AIOS KB warns this misreports correctly-priced
  listings and the shipping source is not yet identified. **Rank, do not reprice.**
- **Sunsone (`so_926407`) and Retro LED (`re6865`)** account names are **inferred**, not confirmed by Thinesh.
- **Amazon ×0.90 = base ×1.08** vs the documented eBay target base ×1.10 — reconcile with Thinesh.
- **Priority £5/£2 cutoffs** are the developer's (Q6 gave a direction, not numbers).
- **Q8 two new status values** (`PRICE_TOO_HIGH`, `PRICE_SOURCE_MISSING`) are **not** in the production
  catalog — needs Sajeesan.
- **No reviewer sign-off** (Sajeesan / Tamil Selvan) and **no Thinesh final sign-off** yet.
- **FX** for the German (EUR) accounts is undefined.
