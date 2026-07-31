# PRJ-2026-018 · B2B Session Drop Tracker — Germany / Amazon.de (`bsdt`)

Watch-list catching **Amazon.de ASINs whose B2B (business-customer) traffic dropped** between two
matching 30-day windows. Tiers each ASIN by **B2B Sessions** volume (not the unreliable low-volume
B2B Conversion %) and assigns a fixed per-tier action. **528 ASINs** in the source sheet
(Tier 1 Low 506 · Tier 2 Moderate 16 · Tier 3 High 4). Start with `PROJECT_HOME.md`.

- 🔴 **Warehouse data is INCOMPLETE for this task.** The right table exists
  (`business_reports.amz_traffic_by_asin`, B2B columns; Germany=`market_place 10`, `sub_source 8`,
  mapping proven) but **68% of sheet ASINs have zero B2B in the DB and 77% report more B2B sessions
  on the sheet than the DB holds all-time** (impossible if DB were the source) — only ~23% even
  potentially reproducible; May 2026 missing from the feed. Sheet was built from a fuller source
  (likely a direct Seller Central export). Detail: `evidence/DATA_SOURCE_ANALYSIS.md`.
- **Source (imported COPY-only + SHA-256):**
  `evidence/source_documents/REQ-21_b2b-session-drop-tracker-de/`
- **Tier/action engine:** editable thresholds (Tier 2 ≥5, Tier 3 ≥10) on the sheet's "Thresholds"
  tab — never hardcode. Tier set by `MAX(prev, current)` B2B Sessions.

**Status:** ONBOARDING — understood + DB-feasibility proven; **not built / not published / not
committed.** Open items (requester, exact window anchor, IDs) in `TASK_REGISTER.md`.
