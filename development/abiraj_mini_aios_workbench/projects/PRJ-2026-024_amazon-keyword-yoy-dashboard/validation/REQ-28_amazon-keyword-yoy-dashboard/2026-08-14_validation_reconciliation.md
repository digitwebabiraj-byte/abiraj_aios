# Validation / Reconciliation — REQ-28-D01 Amazon PPC Keyword YoY Dashboard

**Date:** 2026-08-14 · **By:** abiraj · **Method:** independent re-query of the live DB (a second
query, not the build script) compared to the figures embedded in the delivered dashboard payload.

## 1. Per-market aggregates — EXACT match
Dashboard payload vs independent DB re-query (`keyword_performance_data`, same grain: keyword_id ×
campaign × ad group, impressions > 0 in either window):

| Market | Rows | Cur Sales | Prev-yr Sales | Cur Orders | Prev-rows |
|---|---|---|---|---|---|
| UK | 2202 ✓ | £1,378.69 ✓ | £14,788.32 ✓ | 72 ✓ | 1581 ✓ |
| DE | 406 ✓ | €235.54 ✓ | €2,556.84 ✓ | 11 ✓ | 369 ✓ |
| FR | 218 ✓ | €123.17 ✓ | €1,312.29 ✓ | 6 ✓ | 193 ✓ |
| IT | 87 ✓ | €71.27 ✓ | €600.24 ✓ | 3 ✓ | 84 ✓ |
| CA | 177 ✓ | $0 ✓ | $1,727.73 ✓ | 0 ✓ | 177 ✓ |
| US | 10 ✓ | $0 ✓ | $0 ✓ | 0 ✓ | 10 ✓ |

Sales, orders, prior-year, row counts and prev-rows reconcile exactly across all six markets.

## 2. Row-level spot check (UK top-5 by current sales) — EXACT match
`spider lights` £181.62 / 5 orders / bid £0.29 · `kitchen light shade` £83.32 / 4 · `pendant light`
£64.50 / 5 / £0.22 · `industrial 3 light pendant` £61.06 / 2 / £0.40 · `rope light` £59.57 / 3 —
all cent-for-cent identical between the DB and the payload, including bid and status.

## 3. Integrity checks — PASS
No negative metrics; no empty keyword text; currency/market mapping correct (UK→GBP/23, US→USD/24,
CA→CAD/26, DE→EUR/10, FR→EUR/9, IT→EUR/14).

## 4. Findings & resolution
- **"95 duplicate keyword rows" — FALSE FLAG, FIXED.** Those rows are the *same keyword text*
  targeted as BROAD/EXACT/PHRASE — distinct `keyword_id`s shown in the Match Type column, not
  duplicates, and nothing was collapsed (all 2,202 rows displayed). The spec's DQ duplicate check
  keyed on keyword+campaign+adGroup only; the delivery layer now makes it match-type-aware. DQ panel
  is all-green; no metric changed. (commit `7f7e463`)
- **Live-accruing drift (expected, not an error).** Between the 10:39 snapshot and the re-query,
  UK impressions/clicks/spend moved slightly (230,066→229,957 impr; 1,448→1,450 clicks; £518.26→
  £518.78) because `keyword_performance_data` keeps syncing and Amazon restates recent days. Sales,
  orders and prior-year figures were stable. A snapshot is a point-in-time capture by design.

## Verdict
**GREEN — all displayed data reconciles to the live database.** Sales / orders / YoY / counts exact;
the only blemish (a coarse duplicate heuristic) is fixed; remaining drift is expected snapshot
behaviour on live-accruing columns.
