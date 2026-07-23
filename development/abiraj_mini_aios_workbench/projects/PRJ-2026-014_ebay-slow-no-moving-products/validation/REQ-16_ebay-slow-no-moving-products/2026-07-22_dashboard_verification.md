# Dashboard Verification — REQ-16-D01 eBay Slow Moving & No Moving Products

**Date:** 2026-07-22 · **Artefact:** `evidence/final_outputs/REQ-16_.../REQ-16-D01_esnm_dashboard.html`
**Harness:** `validation/REQ-16_.../verify_esnm_d01.py` (re-runnable)
**Result:** 🟢 **GREEN — 17/17 data checks and 9/9 UI checks passed, 0 failures.**

---

## Method

The harness re-derives every figure **directly from the two live databases** and from the shipped
workbook, then diffs against the JSON payload the dashboard actually renders. It deliberately does
**not** import `build_esnm_d01.py`, so a bug in the builder cannot mask itself by being reused in
its own test.

---

## 1. Payload integrity

| Check | Result |
|---|---|
| HTML embeds valid JSON | ✅ |
| Embedded rows identical to `esnm_d01_data.json` | ✅ 11,156 |
| `Watchers` absent from dashboard markup/CSS | ✅ |
| File size | 2.97 MB, self-contained |

## 2. Scope vs live DB

| Check | Dashboard | DB | Result |
|---|---|---|---|
| Row count | 11,156 | 11,156 | ✅ |
| Unique `item_id` | 11,156 | — | ✅ no duplicates |
| Account × marketplace counts | 16 combinations | 16 | ✅ all match |

## 3. Aggregates vs live DB

| Metric | Dashboard | DB | Result |
|---|---|---|---|
| Zero 90-day sales | 8,067 | 8,067 | ✅ |
| Dead-stock listed qty | 1,243,866 | 1,243,866 | ✅ |
| Rule 1 count vs zero-90d | 8,067 = 8,067 | — | ✅ equal by definition |

## 4. Random 25-listing field-by-field

Seeded sample (`seed=20260722`), ~15 fields each — SKU, title, price, currency, stock, 7/30/90-day
sales, same-period-last-year, views, site, plus the derived trend, days-since-last-sale and
conversion rate — checked against **both** databases.

**0 mismatches across ~375 field comparisons.**

## 5. Dashboard vs shipped workbook

| Check | Result |
|---|---|
| xlsx rows == dashboard rows | ✅ 11,156 |
| Sampled rows: action, 90-day sales, stock identical | ✅ 0 differences |

The two renderers share `fetch()`/`assemble()`, so this confirms they have not drifted.

## 6. Gap discipline — the checks that matter most

| Check | Result |
|---|---|
| `Watchers` null on every row | ✅ 11,156 / 11,156 |
| Rule 6 assigned to 0 listings | ✅ (no data source) |
| Rule 10 assigned to 0 listings | ✅ (known Rule-1 shadowing) |
| Missing traffic renders **blank, never 0** | ✅ 9 blank vs 1,658 genuine zeros |

That last line is the important one: **9 listings have no traffic row** (blank) and **1,658 have a
real measured zero**. The two are correctly distinguished — collapsing them would make Rule 9 fire
on listings that were never measured.

## 7. Rendered UI (live browser)

| Check | Result |
|---|---|
| 20 columns, no Watchers header | ✅ |
| 11,156 rows loaded | ✅ |
| Theme opens **light** | ✅ |
| No horizontal page overflow | ✅ |
| Frozen Image/Account columns `position: sticky` | ✅ |
| Thumbnails loading from eBay CDN | ✅ |
| Priority edge bars present | ✅ |
| Deep scroll (end of virtualised list) renders | ✅ |
| Console errors | **0** |

## 8. Filter ↔ card agreement, cross-checked to the DB

| Filter | Rows | KPI card | Critical | DB agrees |
|---|---|---|---|---|
| SunSone – UK | 1,148 | 1,148 of 11,156 | 766 (66.7%) | ✅ |
| LEDSone – UK | 2,838 | 2,838 of 11,156 | 1,967 (69.3%) | ✅ |
| Coventry Lights – UK | 536 | 536 of 11,156 | 334 (62.3%) | ✅ |
| Germany | 3,471 | 3,471 of 11,156 | 2,668 (76.9%), 6 of 16 accounts | ✅ |
| *(reset)* | 11,156 | 11,156 | 8,067 (72.3%) | ✅ |

Cards and table never disagree, and every figure reconciles to the database.

---

## Defects found and fixed during this build

| # | Defect | Status |
|---|---|---|
| 1 | **KPI cards never updated on filter** — computed once at load, so a filtered table sat beside whole-portfolio totals. Anyone screenshotting a filtered view would have reported the wrong number. | **FIXED** — cards recompute from the filtered view |
| 2 | **Sort dictionary off-by-one** — the map pointed at column indices 19/20, which did not exist. "Action Required" sorted against the *status* lookup and produced nonsense order. | **FIXED** — verified sorting now groups actions correctly |
| 3 | **Image column fell back to the listing URL** when no product image existed — fine as a workbook hyperlink, but would render as a broken image in the dashboard. | **FIXED** — separate `img_only` field |
| 4 | **Thumbnails loaded the full-size `s-l1600` asset** (up to 385 KB) for a 42 px cell. | **FIXED** — `s-l225` (~17 KB, 23× smaller) |
| 5 | **`loading="lazy"` on thumbnails** was redundant against virtualisation and delayed them. | **FIXED** — eager for the ~25 on-screen rows |
| 6 | **"£14.2M value at risk" presented as a headline** — it is eBay *published* quantity × price, not physical inventory. | **RELABELLED** — marked ✻ with the caveat on the card, the Stock header and the footer |

---

## What this verification does NOT establish

Stated so the GREEN is not over-read:

1. **The 20-column dashboard diverges from the 21-column workbook.** `Watchers` was removed
   from the dashboard on the owner's instruction; **the workbook still carries all 20** with the
   column blank. A reviewer will notice. Should be recorded against decision **A**.
2. **Rule precedence remains an unconfirmed assumption** — it is what makes 8,067 listings read
   "End Listing".
3. **Rule 8's £5.00/30-day threshold is invented** — the source defines "high" nowhere.
4. **Views are knowingly understated** (~23% over the 30-day window) from 11 lost ingestion days.
   Rules 5 and 9 are correct *given the data present*, not given complete data.
5. **Stock is eBay published quantity**, not physical inventory.
6. **No business review has occurred** — Thinesh has not seen the output.
7. **No visual screenshot was captured** — the browser pane would not composite frames in this
   environment. All UI checks are DOM/computed-style measurements, which prove structure and data
   but not aesthetic judgement.

---

## Verdict

🟢 **GREEN — the dashboard renders correct data.** Every figure it displays, filtered or unfiltered,
reconciles to the live databases and to the shipped workbook. Gap handling was tested specifically
and the report never fabricates a measurement.

**AMBER for sign-off**, unchanged: three business assumptions are still open (decisions A, C, G) and
no reviewer has approved it.


---

## Post-verification changes (recorded 2026-07-22, after this run)

This record captures the state at verification time. Three changes landed afterwards and are
**not** covered by the 17/17 result above:

1. **`Same Period Last Year` split into `LY 30d` and `LY 90d`** — the dashboard is now 20 columns
   and the workbook 21. Both comparators were spot-checked against the live DB
   (item `395837704497`: LY-30d **9**, LY-90d **28**, matching a hand trace of the order lines).
2. **Sales Trend dashes filled** — `0%` where both windows are zero (6,768 rows), **▲ NEW** where
   last year was zero but this year sold (1,504 rows). Zero dashes remain; 0 formula errors.
3. **Published to ph_task 411-414** (`ebay_priors`, v4) — see `PROJECT_HOME.md`.

**The harness is re-runnable and should be re-run before sign-off** to re-verify against the
current artefact:

    python validation/REQ-16_ebay-slow-no-moving-products/verify_esnm_d01.py
