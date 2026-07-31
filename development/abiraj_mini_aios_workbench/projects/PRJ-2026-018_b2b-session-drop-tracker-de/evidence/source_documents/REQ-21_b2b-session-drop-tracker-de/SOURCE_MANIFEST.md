# SOURCE MANIFEST — REQ-21 (B2B Session Drop Tracker · Amazon.de)

Imported COPY-only (originals untouched), verified by SHA-256.

| File | SHA-256 | Delivered by | Imported |
|---|---|---|---|
| `B2B_Session_Drop_Tracker_DE.xlsx` | `f9cc85ba9503800885358dfaf44e1b119dc27402ac258a9210551ffab467fc6e` | Owner (Downloads) | 2026-07-31 |

## Contents (3 tabs)
- **Objective & Guide** — narrative: source = Amazon Seller Central Business Reports (Detail Page
  Sales and Traffic by Child Item), Amazon.de, two 30-day windows; B2B-only columns; objective;
  per-column usage; tier-driven Status/Action.
- **Thresholds** — editable Tier 2 / Tier 3 B2B-session boundaries (blue input cells) + the 3-tier
  action table. **Canonical for the engine — never hardcode thresholds.**
- **Tracker** — the built output: header row + **528 ASIN rows**, 12 columns.
  Tier distribution: Tier 1 Low 506 · Tier 2 Moderate 16 · Tier 3 High 4.

Verify: `sha256sum -c SHA256SUMS.txt` in this folder.
