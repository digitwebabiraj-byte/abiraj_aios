# Merged Dashboard — eBay Listings (EPPR + ESNM)

**What this is:** a *combined view* of two tasks that already exist and run on their own:
- **EPPR** — eBay Product Performance (PRJ-2026-016)
- **ESNM** — eBay Slow / No-Moving (PRJ-2026-014)

It puts both on **one page with tabs**, joined by eBay **Item ID** (one row per listing).
Pick a tab → see that task's columns next to a shared identity block on the left.

**Important — this does NOT touch the two source tasks.**
- The builder only **reads** each task's finished output file (read-only):
  - `PRJ-2026-016_.../evidence/final_outputs/REQ-19_.../eppr_d01_data.json`
  - `PRJ-2026-014_.../evidence/final_outputs/REQ-16_.../esnm_d01_data.json`
- EPPR and ESNM keep running their own automations their own way. Nothing here changes them.

**No new data.** Same numbers the two tasks already produced — just shown together.

## How to rebuild
```
python build_ebay_listings_merged.py
```
Produces `merged_eppr_esnm_dashboard.html` (open in a browser).

## Status
- **Not automated.** This is a manual build for review. It shows a snapshot of whatever
  each task last produced (EPPR window 2026-06-28→07-27, ESNM anchor 2026-07-31).
- If we later want it to refresh itself, it needs its **own** small scheduled job that runs
  *after* both source tasks — a separate decision, not done yet.
