# closure / REQ-24 — SIGNED OFF

**REQ-24-D01 Channel Opportunity — ACCEPTED / SIGNED OFF by Mahima (Business Validator) on 2026-08-05.**

## What was accepted
The Channel Opportunity report for Germany — one row per clean base SKU with Shopify / Amazon / eBay
**units** side by side, an **Opportunity** class (Missing channel / Marketplace winner / Shopify winner) and a
recommended **Action**. **283 opportunity rows** (270 Missing channel · 10 Marketplace winner · 3 Shopify
winner) from 2,436 base SKUs, sourced READ-ONLY from the raw `mcp.ledsone` `order_management` schema and
reconciled against the live DB.

- **Excel:** `evidence/final_outputs/REQ-24_.../REQ-24-D01_channel_opportunity.xlsx`
- **Interactive dashboard:** `…/REQ-24-D01_channel_opportunity.html` (+ Download-CSV, full-screen)
- **Published:** `tech_team_outputs.ph_task` id **699** (Mahi / `german_priors`), v7, md5-verified.

## Accepted rule set (the previously-provisional defaults, now confirmed)
Market = Germany · metric = **UNITS** · window = rolling **90 days** · FLOOR = 10 · Missing = 0 units in ≥1
channel · Shopify-winner ≥50% · Marketplace-winner ≥60% & Shopify ≤20% · combos kept in.

## Status
🟢 **CLOSED — signed off 2026-08-05.** No open blockers. Optional future work (not part of this sign-off):
weekly automation (fmp pattern), a UK/all-market variant, or a revenue view — each on request.
