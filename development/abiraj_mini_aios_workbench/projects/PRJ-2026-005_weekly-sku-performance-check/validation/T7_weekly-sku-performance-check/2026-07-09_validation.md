# Validation — Table 7 Weekly SKU Performance Check (D01)

- **Date:** 2026-07-09
- **Task:** T7_weekly-sku-performance-check · D01
- **Window:** 2026-07-02 → 2026-07-08 (rolling 7 days, Thursday run)
- **DB:** `order_management_copy` (live production, read-only via Postgres MCP)
- **Validator:** Abiraj (executor). Reviewer sign-off (Sajeesan · Tamil Selvan) + Thuwaraga review pending.

## 0. IMPORTANT — the source DB is live; counts are a point-in-time snapshot

The first build (~12:00 Asia/Colombo) read **150** window orders; a re-check at **14:17** read
**170** — the all-time listing universe also grew 2,132 → 2,158 in that interval. The window is
closed (latest order 08-Jul 23:49) yet the numbers moved, i.e. **marketplace orders keep settling
(late channel sync / status flips to `Completed`) for ~1–2 days after a window ends.** Nothing is
wrong with the logic — a Thursday-morning run for a Wednesday-ending window firms up over the next
day or two. **Every run must therefore be stamped with its snapshot time** (now shown in the
dashboard header, xlsx subtitle and `data.json.meta.snapshot_at`). This report = snapshot
**2026-07-09 14:17 Asia/Colombo**.

## 1. Pre-flight rule checks (verified against live DB)

| Check | Result |
|---|---|
| PH spelling | single variant `thuwaraga` (27k+ rows); "thuwaraka" absent. ✔ |
| UK platforms | `AMAZON, B&Q, EBAY` for `market_place='UK'`. ✔ |
| Order metric | `COUNT(DISTINCT order_item_info)` where `order_status='Completed'`. ✔ |
| Listing↔registry join | on `sku` (best coverage) — used. ✔ |
| Product name | title else category → 0 rows with empty name. ✔ |

## 2. Independent cross-check (does NOT reuse the report pipeline)

A plain direct query — no universe/LEFT-JOIN/grouping logic — must equal the report:

```sql
SELECT source_name, COUNT(DISTINCT order_item_info) AS orders
FROM public.order_transaction
WHERE LOWER(user_name)=LOWER('thuwaraga') AND market_place='UK'
  AND source_name IN ('AMAZON','EBAY','B&Q') AND order_status='Completed'
  AND order_date::date BETWEEN DATE '2026-07-02' AND DATE '2026-07-08'
GROUP BY source_name;
```

Result @ 14:17 snapshot: **Amazon 122 · eBay 27 · B&Q 21 = 170** — matches the report exactly.

## 3. Reconciliation (report @ snapshot 2026-07-09 14:17)

| Metric | Direct SQL | data.json / HTML | xlsx |
|---|---|---|---|
| Window orders (total) | 170 | 170 | 170 |
| Amazon / eBay / B&Q | 122 / 27 / 21 | 122 / 27 / 21 | 122 / 27 / 21 |
| Listings performing | 110 | 110 | 110 |
| Listing rows (report, `amzn.gr.*` excl. 18) | — | 2,140 | 2,140 |
| Product families / active | — | 218 / 43 | 218 |
| Families merging >1 SKU (`+N SKUs`) | — | 138 | 138 |

## 4. Spot checks

- `LDMG125E278` top family — orders tie to the per-listing detail. ✔
- B&Q listing (ref NULL) rendered as `Row Type = B&Q SKU`. ✔
- Purple-summary maths (X/Y, platform sums) recomputed from blue rows independently — consistent. ✔

## 5. Data-quality flags surfaced (not silently resolved)

- **SKU-family grouping = merge by product** (owner-confirmed 2026-07-09). Base SKU + pack-size
  variants rolled up; suffix stripped only when the base is a real universe SKU (anchored,
  reversible). 138/218 families merge >1 SKU (tagged `+N SKUs`) — reviewer to spot-verify.
  `mapped_sku` not used for grouping (dirty). Spot: `LDMG80B224` = base + 2PK/3PK/5PK/6PK/APK →
  1 family, 35 listings (matches the template's `LDMG80B224` example structure).
- **18 `amzn.gr.*` pseudo-SKUs** — Amazon internal group IDs, excluded (all zero-order).
- **Zero-order sprawl** — 2,030/2,140 listings at 0 (idle cross-listings); dashboard defaults to
  Active families.
- **Live-snapshot drift** — see §0; report carries an `as of` timestamp.

## 6. Result

**PASS (build + reconcile).** The report ties exactly to an independent direct DB query at the same
snapshot instant; no figure invented; all risks flagged. **Open before closure:** owner decision on
`mapped_sku` grouping; delivery channel + Thursday scheduling (with dynamic window); whether to run
later in the day so the window has settled; reviewer sign-off + Thuwaraga review.

**Decision: GREEN on the build; AMBER on closure.**
