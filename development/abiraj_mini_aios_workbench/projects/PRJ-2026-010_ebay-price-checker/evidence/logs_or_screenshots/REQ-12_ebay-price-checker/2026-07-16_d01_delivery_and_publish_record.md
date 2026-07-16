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
- **Initial row (id 264, Thinesh):** `project_code=epc` · `task_id=epc_Thinesh_ebay_price_checker-V1` ·
  `assigned_user=Thinesh` · `assigned_user_team=ebay_priors` · `team=Development` · `developer=Abiraj` ·
  `phase_level=1` · `version_status=released` · `html_content` = 17 MB dashboard. The first attempt failed
  at `connect` ("too many clients"/"slots reserved for superusers") and wrote nothing; a retry committed.
  The dry-run consumed identity id 263 (sequences don't roll back).
- **Dashboard refreshed to version 3** via two guarded in-place `UPDATE`s: V2 = taller-table fix (portal
  panel gave `100vh` too little height); V3 = the **Export-CSV button** (client-side, exports the current
  filtered/sorted view, UTF-8 so £/€ render in Excel). `description` also trimmed to 289 chars.
- **Fan-out publish 2026-07-16 — 3 more users (ids 299–301), same guarded pattern.** After owner
  confirmation (team `ebay_priors`, full report), verified the names live against `staff.users`
  (`Jarsini` id 91, `kobiga` id 157, `powsteena` id 162 — all Active; note **`Jarsini` ≠ `Jasmini`**, two
  different people), pre-flighted all 3 `task_id`s free, dry-ran + rolled back, then inserted 3 rows in one
  transaction:

  | id | assigned_user | task_id | team | status |
  |---|---|---|---|---|
  | 264 | Thinesh | `epc_Thinesh_ebay_price_checker-V1` | ebay_priors | released |
  | 299 | Jarsini | `epc_Jarsini_ebay_price_checker-V1` | ebay_priors | released |
  | 300 | kobiga | `epc_kobiga_ebay_price_checker-V1` | ebay_priors | released |
  | 301 | powsteena | `epc_powsteena_ebay_price_checker-V1` | ebay_priors | released |

  All four carry the identical 17 MB V3 dashboard. Independently re-verified via the Postgres MCP: exactly
  **four** `epc` rows, four distinct users, all `ebay_priors` / `released`.
- ⚠ 17 MB exceeds the table's historical max (14 MB); avg row is 370 kB. The portal viewer rendered it;
  a lighter summary build can replace it via in-place `UPDATE` if needed.

## Sign-off — COMPLETE 2026-07-16 (audit trail of the previously-open items)
All items below were resolved and signed off on 2026-07-16 (per owner). REQ-12-D01 is **CLOSED**.
- **Shipping basis** — signed off (Sajeesan / DB owner). ⚠ **Data note that remains true regardless of
  sign-off:** Status is computed on **item price only**; a shipping-aware refresh (should one be scoped)
  is a future REQ-12-D02. The live `ph_task` row descriptions retain the "item-price" note for end users.
- **Sunsone (`so_926407`) / Retro LED (`re6865`)** — identities confirmed (Thinesh).
- **Amazon ×0.90 = base ×1.08 vs the documented eBay target base ×1.10** — confirmed (Thinesh).
- **Priority £5/£2 cutoffs** — confirmed (Thinesh).
- **Q8 two new status values** (`PRICE_TOO_HIGH`, `PRICE_SOURCE_MISSING`) — decided (Sajeesan).
- **FX** for the German (EUR) accounts — confirmed (Thinesh).
- **Reviewer sign-off** — Sajeesan (technical) + Tamil Selvan (queryability) — complete.
