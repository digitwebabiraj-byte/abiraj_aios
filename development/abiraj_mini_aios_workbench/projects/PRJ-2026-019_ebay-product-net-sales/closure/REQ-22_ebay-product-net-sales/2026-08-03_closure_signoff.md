# Closure & Sign-off — REQ-22-D01 eBay Product Net Sales

| Field | Value |
|---|---|
| Project | `PRJ-2026-019_ebay-product-net-sales` · code `epns` |
| Task | `REQ-22` · deliverables D01 (report) · D02 (lookup) · D03 (dashboard) · D04 (automation) |
| **Business sign-off** | ✅ **Kobiga — SIGNED OFF 2026-08-03** (requester / Business Validator) |
| Status | ✅ **CLOSED — DELIVERED · PUBLISHED · AUTOMATED · SIGNED OFF** |
| Git | `main` HEAD `e38dc7a` (pushed) |

## What was accepted
- Per-order eBay **Net Sales (NNV)** report, **settled-only, 4,072 orders**, last 30 days, per marketplace currency.
- **NNV = Gross − Final Value Fee − General (AD_FEE)** — ties to eBay's per-order payout and the source anchor
  `02-14934-76138` → **22.39**. General = Promoted Listings "General" fee; PPC = `PREMIUM_AD_FEES` (CPC, listing-allocated).
- Excel (Net Sales + Order-ID Lookup) + interactive dashboard + static portal HTML.
- **Published** to `tech_team_outputs.ph_task` ids **594–599** (ebay_priors: Thinesh · Jarsini · kobiga · powsteena · Sharmilan · Sivajitha), `assigned_user_team='ebay_priors'`.
- **Automated:** Windows task `EPNS_Weekly_Net_Sales`, every Wednesday 11:30, fail-closed, proven (LastTaskResult 0).

## Flagged estimates (accepted)
- **VAT (20%)** — derived; **Product Cost (20% of price)** — owner-agreed proxy (no real COGS exists);
  **Net Profit [est] = NNV − VAT − Product Cost − PPC**. These are estimates, not booked figures.

## Remaining (non-blocking)
- Varmen to confirm the provisional `REQ-22` / `PRJ-2026-019` / `epns` identity.
- Reviewer gates: Sajeesan (technical), Tamil Selvan (queryability).
- Optional: supply a real COGS source to make Net Profit booked; write `verify_epns_d01.py`.
