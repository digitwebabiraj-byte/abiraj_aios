# Duplicate-risk report — REQ-22 eBay Product Net Sales

Checks whether this Net Sales report overlaps existing deliverables before build/publish. **TODO.**

## Candidates to compare against
- **DST** (PRJ-2026-015) — daily eBay sales by account × marketplace (sales totals, not per-order net).
- **EPPR** (PRJ-2026-016) — per-listing performance (has a cost/profit block, listing grain not order grain).
- **ERA** (PRJ-2026-012) — per-SKU eBay returns.
- **EPPA** (PRJ-2026-013) — eBay PPC pause (source of the CPC+CPS ad-cost method reused here).

Provisional verdict: **distinct** — this is per-**order** Net Sales (NNV) with a full deduction stack and
an Order ID lookup, which none of the above produce. Confirm formally during discovery.
