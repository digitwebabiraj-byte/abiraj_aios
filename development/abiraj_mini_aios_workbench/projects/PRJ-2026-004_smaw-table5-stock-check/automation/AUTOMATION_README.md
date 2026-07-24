# SMAW — Table 5 Weekly Stock Check (Thuwaraga) — automation (REQ-06)

Weekly refresh of Thuwaraga's full-portfolio stock dashboard. Recomputes READ-ONLY from the live
warehouse and refreshes the `ph_task` row (id 137).

## What runs, and when

| | |
|---|---|
| Task | `SMAW_Weekly_StockCheck` |
| When | **Mondays, 08:00** (clear of the 09:30–11:00 cluster) |
| What | every Thuwaraga ASIN×account: UK stock, 90-day velocity, days-remaining, stock status |
| Reads | `public.location_wise_inv_stock` (UK stock), `order_transaction`, `listing_data`, `analytics.ph_segment` — READ-ONLY |
| Writes | 1 row in `ph_task` (`SMAW`, `SMAW_thuwaraga_table5_all_asins-V2`, `assigned_user=thuwaraga`, `ph_priors`) |
| Entry | `run_smaw_weekly.bat` → `smaw_weekly_run.py` → drives the signed-off `build_all_html.py` |

## The method (unchanged from signed-off REQ-06 D03)

Full-portfolio (733+ ASINs). UK stock = `location_wise_inv_stock` (location='UK'). Velocity = 90-day
Completed-FBM units ÷ 90. Days = UK stock ÷ velocity. Status: warehouse 0 → Critical; <15d →
Critical; ≤60d → Going Out; else Healthy. `build_all_html.py` refines "No Stock / Critical" into real
**stockouts** (sold + 0 stock) vs **inactive** (dead). The SQL anchors on `CURRENT_DATE` — run-date
safe, no parameterization. 13 SQL columns map 1:1 to the dashboard row keys.

## Two things the runner handles (see the code comments)

1. **`temp_user` has no `supplier` schema access.** The 3 incoming columns
   (po_qty/suppliers/containers) were all-NULL in the live V2 anyway (0 of 756 rows), so the runner
   stubs the supplier-reading CTE — identical result, zero data loss, fails closed if the CTE moves.
2. **First run refreshes stale stock.** The live V2 was built while the inventory feed was frozen at
   2026-05-04; the feed is live again, so the first automated run legitimately moves stock numbers to
   current (dry-run: 776 rows / 121 critical / 245 healthy vs 756 frozen). Expected — the report was
   two months stale.

## Publish grain — WEEKLY REPLACE

`task_id = SMAW_thuwaraga_table5_all_asins-V2` (id 137), updated in place each week (backup-first,
md5-verified). One row, always current.

## Gates (fail-closed)

Row floor (`SMAW_MIN_ROWS`) · collapse-vs-last-good (40%) · md5 before commit. Exit `2` = a gate
failed, nothing published, last week's dashboard stays live.

## Everyday use

```bat
run_smaw_weekly.bat --dry-run   :: recompute + build, write NOTHING (safe)
run_smaw_weekly.bat             :: a real weekly refresh, now
```

On failure `SMAW_ALERT_FAILED.txt` appears on the Desktop and clears after the next success.

## Open items (unchanged by automation)

Reviewer sign-off (Tamil Selvan / Sajeesan) + Thuwaraga's stockout/inactive labelling confirmation;
4 legacy→canonical SKU rows flagged `LEGACY?` (flag, don't auto-correct — no mapping source exists);
the 4 parked D01 fields (FBA on-hand, container ETA, W1/W2/W3 mapping, last-checked date).

## Related

Same pattern + credential store as the rest of the fleet.
