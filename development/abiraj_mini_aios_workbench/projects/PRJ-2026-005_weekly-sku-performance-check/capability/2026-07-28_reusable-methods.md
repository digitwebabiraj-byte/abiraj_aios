# Table 7 Weekly SKU Performance Check — Reusable Methods (Capability Extract)

> Reusable, generalisable techniques extracted from PRJ-2026-005 (Weekly SKU Performance Check,
> Table 7 for PH Thuwaraga). These are methods a future eBay/Amazon reporting project could
> reuse — not project-specific facts.
> **Sources:** `PROJECT_HOME.md`, `SYSTEM_REFERENCE.md`,
> `validation/T7_weekly-sku-performance-check/2026-07-09_validation.md`,
> `automation/AUTOMATION_README.md`.

## What this project does
Every Thursday, groups a Portfolio Holder's UK listings (Amazon / eBay / B&Q) by resolved base
SKU and shows a rolling 7-day **Completed**-order count per platform, flagging every listing with
zero orders — a dead-listing / performance check, DB-derived, no weekly re-keying.

## Reusable rules / methods

1. **Rolling window computed dynamically, never hard-coded.** `ws = (CURRENT_DATE - INTERVAL
   '7 day')::date`, `we = (CURRENT_DATE - INTERVAL '1 day')::date`; filter on `order_date::date
   BETWEEN ws AND we`. A scheduled job needs no dates edited each cycle.

2. **Order metric = `COUNT(DISTINCT order_item_info)` where `order_status='Completed'`.** Count
   distinct order items, not rows; restrict to Completed so pending/cancelled don't inflate.

3. **Listing reference = `COALESCE(NULLIF(asin,''), NULLIF(item_id,''))`.** ASIN for Amazon,
   `item_id` for eBay; NULL for B&Q, which is grouped on `sku` and labelled `B&Q SKU`. One
   pattern spans three marketplaces.

4. **Join order→registry on `sku`, not on the ref.** `order_transaction.sku = listing_data.sku`
   gave best coverage (2,401/2,448 vs 2,194 on ref). Always measure join coverage both ways
   before picking the key.

5. **LEFT JOIN keeps zero-order listings as 0.** Build the listing universe first (DISTINCT
   sku/ref/source/account), then LEFT JOIN this-week's counts so idle listings survive as 0
   rather than being dropped — essential for a dead-listing report.

6. **Product name = title else category fallback.** `listing_data.title` if present, else
   `MODE(order_transaction.category_name)` per sku — guarantees no empty name.

7. **Anchored, reversible SKU-family grouping.** Merge pack-size variants under a base SKU by
   stripping a recognised suffix (`\d+PK`/`APK`/`PCK\d+`) **only when the stripped base is itself
   a real SKU in the universe**. Never invents a relationship; families rolling up >1 SKU are
   tagged `+N SKUs` for human verification.

8. **Presentation kept out of SQL.** SQL returns grain + numbers; the renderer applies colour
   bands and the two-tier layout (blue per-listing detail rows, purple per-family summary rows).

9. **Independent cross-check at the same snapshot instant.** Reconcile the report against a plain
   direct `COUNT(DISTINCT order_item_info)` query (no universe/join/grouping logic) taken at the
   same moment — the report must tie exactly.

## Gotchas / traps

- **Live DB — counts are a point-in-time snapshot.** The same window read 150 orders at 12:00 and
  170 at 14:17; marketplace orders keep settling (late sync / status flips to Completed) for ~1–2
  days after a window closes. Stamp every run with its snapshot time; cross-checks must use the
  same instant.
- **Settle buffer (OPEN, owner decision).** Re-running D01's own window 12 days later added +13
  orders (7.1%), every one an increment on a listing already reported — a T+1 run undercounts.
  Moving the window end earlier changes the numbers, so it is a Business-Validator call, not a
  silent fix. (FRRC hit the same ~12% class of issue.)
- **`mapped_sku` is dirty — do NOT group on it.** It reassigns some listings cross-family (a G95
  bulb → a C35 candle base). Rule is "mapped_sku else sku" only for resolution; such rows are
  tagged `MAPPED?` and left for verification.
- **`amzn.gr.*` pseudo-SKUs (18) are Amazon internal group IDs, not products** — all zero-order;
  excluded by the renderer but kept in SQL for auditability.
- **Zero-order sprawl misreads as faults.** ~95% of listings show 0 due to idle cross-listings
  (relistings, multi-account, retired ASINs); default the dashboard to Active families so the red
  band isn't read as thousands of real faults.
- **PH spelling trap.** Sheet spells "Thuwaraha"/"Thuwaraka"; the only DB variant is `thuwaraga`
  — filter `LOWER(user_name)='thuwaraga'`.
- **Product name quality.** Some `listing_data.title` values are variant option labels ("Ten",
  "Paquet de 6") rather than full titles; category fallback fills blanks.

## Key sources
- `public.order_transaction` — orders + listing universe (one row per line item). Columns:
  `user_name`, `market_place`, `source_name`, `sku`, `asin`, `item_id`, `order_item_info`,
  `order_status`, `order_date`, `category_name`, `ss_name`. Filter `market_place='UK'`,
  `source_name IN ('AMAZON','EBAY','B&Q')`.
- `public.listing_data` — SKU/ASIN registry. Columns: `sku`, `mapped_sku`, `title`, `wrong_sku`
  (always `= 0`).
- Publish target: `tech_team_outputs.ph_task` (DB `order_management_copy`), single governed row
  id 135 (`project_code=WSPC`, `assigned_user_team=ph_priors`, `version_status=released`).

## Automation pattern
- **Task `T7_Weekly_SKU_Performance`, every Thursday 11:00** via `automation/run_t7_weekly.bat`;
  11:00 keeps it clear of other jobs sharing the restricted `temp_user` account.
- **Five stages, fail-closed:** `pull → validate (FAIL CLOSED) → render → guarded publish → log`.
  Every gate runs before any write; any failure ⇒ non-zero exit and nothing published, so the
  last good dashboard stays live.
- **Gates:** zero-rows/floor (`T7_MIN_ROWS`, default 500), unexpected platform, negative/missing
  SKU, duplicate listing key, control total vs a direct `COUNT(DISTINCT order_item_info)`, family
  count / dashboard size, **md5 of stored HTML before commit** (rolls back on corruption),
  routing (`ph_priors` + `released`) intact after write. Exit codes 0/1/2/3/4.
- **Renders the signed-off `build_html.py` — never re-implemented.** Refreshes `ph_task` row 135
  in place (guarded single-row write; no other row touched).
- **Regression test = containment, not equality.** `--dry-run --window 2026-07-02` asserts every
  one of D01's 2,140 listings is still produced (a lost row = query drift), but deliberately does
  NOT assert headline totals, since settle drift legitimately moves them.
- **Credentials:** one DB; `PGPASSWORD` from the global store
  (`05_documentation/capability/shared_db_credentials/`); no password default — unset ⇒ abort
  before writing. Failure drops `T7_ALERT_FAILED.txt` on the Desktop (self-clears on next success).
- Same pattern as PRJ-2026-010 (EPC) and PRJ-2026-008 (FRRC); method doc
  `05_documentation/capability/2026-07-15_monthly-report-automation-pattern.md`.
