# Data Source Analysis — B2B Session Drop Tracker (Amazon.de)

**Date:** 2026-07-31 · **Verdict:** 🔴 **NOT REPRODUCIBLE FROM THE WAREHOUSE AS-IS — the DB is
INCOMPLETE for this task.** The correct *column mapping* exists, but the *B2B traffic coverage* is
missing for ~77% of the sheet's ASINs (see "Completeness test" below). Right table, wrong (partial) data.

> ⚠️ **Correction to first-pass onboarding.** The initial note said "fully reproducible" based on one
> ASIN (`B0DLWRP73C`) reconciling to the unit. That single exact match validated the **column mapping
> only** — it did **not** prove coverage. A full 526-ASIN completeness test (below) shows the warehouse
> holds only a fraction of the B2B traffic the source sheet was built from.

## Question
The source sheet says it was built from *Amazon Seller Central Business Reports → Detail Page Sales
and Traffic by Child Item* for Amazon.de. Is that B2B data in the internal DB, or is this an external
export (as eckr / PRJ-2026-017 turned out to be)?

## Finding
The B2B Business-Reports metrics exist natively in the warehouse table
**`business_reports.amz_traffic_by_asin`** (43 columns, 125,792 rows, 2025-01-01 → 2026-07-25). A
column search (`ILIKE '%b2b%'`) returned 17 B2B columns including everything the tracker needs:
`sessions_b2b`, `page_views_b2b`, `units_ordered_b2b`, `buy_box_percentage_b2b`.

## Column mapping (sheet → DB)
| Sheet | DB column | Notes |
|---|---|---|
| ASIN | `child_asin` | sheet is child grain |
| B2B Sessions | `sessions_b2b` | *Sessions · Total · B2B* |
| B2B Page Views | `page_views_b2b` | *Page Views · Total · B2B* |
| B2B Orders | `units_ordered_b2b` | *Units ordered · B2B* |
| Buy Box % | `buy_box_percentage_b2b` | current window only |

## Scope filters (proven)
- **Germany** = `market_place = 10` (`order_management.market_place`: id 10 = Germany, DE,
  amazon.de, `A1PA6795UKMFR9`).
- **Account** = `sub_source = 8` (amazon Ledsone). DE B2B rows exist only under sub_source 8;
  sub_source 6/9 carry no DE B2B data in this table.
- **Windowing** = two 30-day ranges on `date` (Prev vs Current).

## Reconciliation (unit-exact)
Reference ASIN **`B0DLWRP73C`** (market_place 10, sub_source 8): the DB holds **19** total
`sessions_b2b` across its history (17 session-days, 2025-10-04 → 2026-04-14). The source sheet shows
**Prev 15 + Current 4 = 19**. Exact match → the mapping and filters are correct.

## Completeness test (526 sheet ASINs vs DB all-time B2B sessions, DE / sub_source 8)
The source sheet includes an ASIN only if it had B2B traffic in ≥1 window, so **every** sheet ASIN's
two-window B2B-session total must be **≤** that ASIN's all-time DB B2B sessions *if the DB were the
source*. It is not:

| Metric | Count | % of 526 |
|---|---|---|
| Sheet ASINs with **zero** B2B sessions in the DB (all-time) | **359** | 68.2% |
| Sheet ASINs where **DB all-time < sheet 60-day total** (impossible if DB were the source) | **406** | 77.2% |
| Sheet ASINs where DB all-time ≥ sheet total (could *possibly* reproduce) | **120** | 22.8% |

Also: **51** of the 527 sheet ASINs are absent from the table entirely; only **167** appear with any
DE B2B activity ever; **May 2026 is completely missing** from the DE feed and Jun/Jul 2026 are nearly
empty (103 / 63 rows). Example impossibilities: `B0CGRNLLPR` sheet 11 vs DB 3; `B0DQD74HVG` sheet 8 vs
DB **0**; `B098XP85Y7` sheet 6 vs DB **0**.

**Conclusion:** the warehouse `business_reports.amz_traffic_by_asin` is a **partial / under-counted**
capture of Amazon.de B2B traffic — at best ~23% of the sheet is reproducible, and even that is an
upper bound (the windowed match would be lower still). The sheet must have been built from a **fuller
source** — most likely a direct Amazon Seller Central Business Reports export, not this warehouse table.

> ✅ **CONFIRMED by owner 2026-07-31:** the requirement Excel was generated **from a direct Amazon
> (Seller Central Business) report export** — not the database. So the DB is NOT the source; the
> owner-supplied Amazon report is the system of record, and this task is built FRRC-style (enrich the
> export). The DB's partial mirror is left as-is (a separate sync-gap issue for Sajeesan if wanted).

## Consequence for the build
This is **NOT** a clean DB→report pipeline like FRRC/EBPD/ERA/DST/EPPR. Before any build:
1. **Find the real source.** Ask the owner where the sheet's B2B numbers came from (direct Seller
   Central export? a different/fuller table? another DB?). If it's a manual Seller Central export,
   this becomes an FRRC-style "enrich an owner-supplied export" task, not a warehouse pull.
2. **Or fix the feed.** If the warehouse *should* hold this data, the DE Business-Reports B2B sync is
   broken/incomplete (missing May 2026, sparse Jun/Jul, most ASINs absent) — a data-engineering fix
   owned outside this report. Raise with Sajeesan.
3. The column mapping and Germany/sub_source filters above are correct and reusable once a complete
   source exists.

## Caveat on the window anchor (still open)
Even for the ~23% that could match, the reference ASIN's B2B sessions **end 2026-04-14**, so the
sheet's "Last 30 Days" is **not** anchored to today (2026-07-31). The exact export "as of" date must
be confirmed with the owner.
