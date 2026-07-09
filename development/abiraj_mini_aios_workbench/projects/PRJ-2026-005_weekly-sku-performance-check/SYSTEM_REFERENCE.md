# SYSTEM_REFERENCE — Table 7 Weekly SKU Performance Check

Complete functional detail for the Table 7 weekly report. Derived from the approved spec
(sheet `PH-2026-07-THUW07 - Abiraj`), `HANDOFF_weekly_sku_performance_check.md`, and verified
against the live DB `order_management_copy`. Read this before changing any rule.

---

## 1. What the report answers

Every Thursday, for Portfolio Holder **Thuwaraga**, across her UK listings on **Amazon, eBay
and B&Q**: how many **Completed** orders each listing took in the last rolling 7 days, which
listings sold nothing, and — grouped by base SKU — how many ASINs in each SKU family are
performing. It is a *performance / dead-listing* check, not a stock or revenue report.

## 2. Schedule & report window (business rule)

- **Runs every Thursday.**
- **Window = rolling 7 days ending the day _before_ the run date.** A Thursday run therefore
  covers last Thursday .. last Wednesday (inclusive, on `order_date::date`).
- First live run: **run date 2026-07-09 → window 2026-07-02 .. 2026-07-08.**
- The window must be computed dynamically at run time, not hard-coded:
  `ws = (CURRENT_DATE - INTERVAL '7 day')::date`, `we = (CURRENT_DATE - INTERVAL '1 day')::date`.
  (The current `generate_dataset.sql` pins the snapshot dates with a `<<< set dynamically` marker.)

## 3. Data sources & LOCKED rules (verified against live DB)

| Rule | Value | Verified |
|---|---|---|
| PH filter | `LOWER(order_transaction.user_name) = LOWER('thuwaraga')` | ✔ single variant `thuwaraga`, 27,174 rows; NOT "thuwaraka" |
| Marketplace | `order_transaction.market_place = 'UK'` | ✔ |
| Platforms | `source_name IN ('AMAZON','EBAY','B&Q')` (exclude SHOPIFY, WAYFAIR) | ✔ UK sources present: AMAZON, EBAY, B&Q |
| Order count | `COUNT(DISTINCT order_item_info)` where `order_status='Completed'` | ✔ per handoff |
| Listing ref | `COALESCE(NULLIF(asin,''), NULLIF(item_id,''))` — NULL for B&Q (group on `sku`) | ✔ 2,338/2,448 have a ref; B&Q has sku only |
| SKU family (grouping) | **base SKU + its pack-size variants**, merged in the renderer (owner-confirmed 2026-07-09). Strip a recognised pack suffix (`\d+PK`/`APK`/`PCK\d+`) only when the stripped base is itself a real universe SKU. `mapped_sku` **not** used (dirty). | ✔ e.g. `LDMG80B224` rolls up `…2PK/…3PK/…5PK/…6PK/…APK` |
| Product name | `listing_data.title` if present else `MODE(order_transaction.category_name)` per sku | ✔ 0 rows end with an empty name |
| Join key | `order_transaction.sku = listing_data.sku` (best match: 2,401/2,448 vs 2,194 on ref) | ✔ |

`listing_data.wrong_sku = 0` is always applied. Read-only throughout; no DB object is created.

## 4. Pipeline

1. **Universe** — `SELECT DISTINCT (sku, ref, source_name, ss_name)` from `order_transaction`
   for the PH/UK/platform filter. One row = one listing.
2. **This week's orders** — same filter + `order_status='Completed'` +
   `order_date::date BETWEEN ws AND we`, `COUNT(DISTINCT order_item_info)` grouped by
   (sku, ref, platform, account).
3. **Resolve** — LEFT JOIN base SKU + title (`ld_agg`) and category fallback (`cat`) per sku.
   **LEFT JOIN keeps zero-order listings as 0** (they are not dropped).
4. **Shape (renderer)** — group listing rows into **product families** (base SKU + pack-size
   variants, per §3; suffix stripped only when the base is a real SKU):
   - **Blue "ASIN detail" row** — one per listing. `SKU/ASIN`=sku, `Row Type`=ref (or `B&Q SKU`
     when B&Q/null), single platform column populated, `TOTAL`=that listing's orders,
     `Performing?`=`YES ✅` if >0 else `NO ❌`, `Action`=`Investigate & fix listing` if 0.
   - **Purple "SKU SUMMARY" row** — one per family. Platform columns = sums across the family's
     ASINs; `Performing?` = `✅ All performing` (X=Y) / `X / Y ASINs performing ⚠️` (0<X<Y) /
     `🔴 0/Y performing` (X=0); `Action` = `See ASIN rows below ↓` if X<Y else `—`.
   Colour bands (purple summary / blue detail / green performing / red zero / orange partial)
   are applied by the renderer — kept **out of SQL scope** (same as the Table 5 sibling).

## 5. Output columns (template order)

`SKU / ASIN | Row Type | Product Name | Platform | Account Name | Week Start | Week End |
Amazon Orders | eBay Orders | B&Q Orders | TOTAL Orders | Performing? | Action Required`

Delivered as: an interactive HTML dashboard (KPIs; search; Active / All / Zero-order / Mapped
filters; collapsible SKU groups) and a colour-banded `.xlsx` with the same columns + auto-filter.

## 6. Run snapshot (2026-07-09, window 02-Jul → 08-Jul-2026, **as of 14:17 Asia/Colombo**)

- Universe → **2,140 listing rows after excluding 18 `amzn.gr.*` group-id pseudo-SKUs**
  (all zero-order). **218 product families** (43 active, 175 zero-order; 138 merge >1 SKU).
- **110 listings performing · 2,030 at zero · 170 orders** (Amazon 122 · eBay 27 · B&Q 21).
- **Live-DB caveat:** counts are as-of the snapshot instant. The same query read 150 at 12:00 and
  170 at 14:17 — marketplace orders settle for ~1–2 days after a window closes. Cross-checks must
  use the same instant; see the independent direct-query recipe in the validation note.

## 7. Known limits / data-quality flags

- **Dirty `mapped_sku` (169 listing rows across 47 SKUs).** Where present it can reassign a
  listing to an unrelated family. Handoff rule = "mapped_sku else sku"; such rows are tagged
  **`MAPPED?`** and left for human verification, never auto-corrected. Owner decision pending:
  trust `mapped_sku` vs group strictly by exact `sku`.
- **Zero-order noise.** 95% of listings are 0 because of idle cross-listing sprawl; the dashboard
  defaults to Active families so the red band is not read as ~2,000 real faults.
- **`amzn.gr.*` pseudo-SKUs** excluded (Amazon internal group IDs, not products).
- **Product name** occasionally a variant option label rather than a full title; category fills blanks.
- **Scheduling / delivery channel** not yet decided (open items).

## 8. Regeneration

```
# 1. Re-pull data for the current window (edit the win CTE dates first, or wire CURRENT_DATE):
#    run  sql/T7_weekly-sku-performance-check/generate_dataset.sql  via the Postgres MCP
#    (+ the names/object pull) and refresh evidence/final_outputs/.../data.json
# 2. Rebuild outputs:
python build_html.py     # -> Table7_Weekly_SKU_Performance_Thuwaraga.html
python build_report.py   # -> Table7_Weekly_SKU_Performance_Thuwaraga.xlsx
```
