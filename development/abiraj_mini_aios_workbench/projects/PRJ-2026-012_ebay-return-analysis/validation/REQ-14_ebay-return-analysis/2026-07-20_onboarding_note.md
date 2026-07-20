# Validation — REQ-14_ebay-return-analysis (onboarding note, 2026-07-20)

**Status: NOT YET VALIDATED against the live DB.** This is an onboarding placeholder, not a build
validation. No live query has been run from this workbench and nothing has been published.

## What was verified at onboarding (2026-07-20)
- **Import integrity:** all 6 source files copied byte-for-byte; SHA-256 recomputed post-copy and
  matches the source archive (see `evidence/source_documents/REQ-14_.../SOURCE_MANIFEST.md`).
- **Reference dataset re-read** from `evidence/final_outputs/REQ-14_.../eBay_Return_Analysis_June2026.xlsx`
  (main sheet `A1:S176`, 144 SKU data rows + TOTAL row):
  - Returns (TOTAL) = **153**; blended Return Rate = **0.17729 ≈ 17.7%**.
  - Refund = **£2,937.37**; Return Cost = **£869.39**.
  - Ad Spend = **£1,387.96**; Ad Sales = **£9,343.63**; ACOS = **0.14855 ≈ 14.9%**; ROAS = **6.73x**.
  - All tie to the handoff's stated acceptance criteria.
  - Real account names present: Sunsone, Ledsone, Electricalsone, Ledsone DE, Vintage Interior, Retroled.
- **SQL sanity read** (`sql/REQ-14_.../ebay_return_analysis.sql`): two statements, six editable dates,
  the two `DISTINCT ON` case CTEs, the `transaction_id` SKU bridge, and the CPC+CPS ad union are all
  present as the handoff describes.

## Still required for REQ-14-D01 acceptance (pending owner go)
1. Confirm the `REQ-14` / `ERA` identifiers with the owner.
2. Run statement 1 + statement 2 via the **Ledsone Database MCP** (read-only), export the two TSVs.
3. `build_dashboard.py` → recalc with LibreOffice → **0 recalc errors**.
4. **Diff the fresh build against the reference figures above** — 144 rows / 153 returns / all totals.
5. Record the reconciliation here; obtain Sajeesan (technical) + Tamil Selvan (queryability) + Thinesh
   (business) sign-off before any publish.
