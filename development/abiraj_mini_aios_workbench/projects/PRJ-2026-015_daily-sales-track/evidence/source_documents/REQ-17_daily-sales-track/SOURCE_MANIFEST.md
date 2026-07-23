# Source Manifest — REQ-17 Daily Sales Track

**Project:** PRJ-2026-015_daily-sales-track
**Task:** REQ-17_daily-sales-track
**Imported:** 2026-07-23
**Import method:** COPY only — original left untouched in `C:\Users\digit\Downloads\`

## Files

| File | Bytes | SHA-256 | Role |
|---|---|---|---|
| `Thinesh task (4).xlsx` | 65,067 | `C14CEB454FA10594EAE2FCAFD34D65F478155AC8EAF384F9B03F4F1BB28142B1` | Single-sheet specification: 22-column output shape (row 1) + a 6-row fabricated sample (rows 2–7) + a 9-KPI summary panel (rows 13–22) |

Sheet name: `Daily Sales Track` — the only sheet in the workbook.

**Copy integrity verified at import:** the original and the copy were hashed independently and are
**byte-identical** (same SHA-256, same 65,067 bytes).

## Workbook inventory (every cell read, 2026-07-23)

| Region | Content |
|---|---|
| Row 1 | The 22 column headers — **canonical** |
| Rows 2–7 | 6 sample rows, all dated `2026-07-23` — **fabricated** |
| Rows 8–12 | Empty |
| Rows 13–22 | The 9-KPI summary panel (`KPI` / `Value` header at row 13) — **canonical shape** |
| Rows 23–1000 | Empty (0 non-empty cells) |

**Structural features: none.** No second sheet, no defined names, no tables, no merged cells, no
conditional formatting, no freeze panes, no autofilter, no column widths set.

## The 22 columns (row 1, canonical order)

`Account` · `Date` · `Today's Sales (£)` · `Yesterday Sales (£)` · `Sales Diff (£)` ·
`Sales Growth %` · `Same Day LY Sales (£)` · `Today's Orders` · `Yesterday Orders` ·
`Order Growth %` · `Same Day LY Orders` · `Units Sold` · `Avg Order Value (£)` · `Best Seller` ·
`Active Listing` · `AH Listing` · `AH Listing Sales` · `AH Sales Trend` · `PH Listing` ·
`PH Listing Sales` · `PH Sales Trend` · `Account Sales Trend`

## The 9 KPIs (rows 14–22, canonical)

`Total Accounts` · `Total Sales Today` · `Total Sales Yesterday` · `Overall Growth` ·
`Total Orders` · `Yesterday Orders` · `Order Growth` · `Total Units Sold` · `Average Order Value`

## Canonical-source ruling

There is one file, and its parts carry **different authority**:

- **Row 1 is CANONICAL** for column shape, order and header text.
- **Rows 13–22 are CANONICAL** for the KPI panel's shape.
- **The sample's arithmetic relationships are CANONICAL** for the formula layer — they were
  independently re-derived and are exact (see below).
- **The sample's *values* are FABRICATED** and carry no authority. They may never be used as a
  reconciliation baseline, a test expectation, or a sanity check on live output.

## ✅ Verified at import — the formula layer reconciles 32/32

Unlike REQ-16's source, whose sample contradicted its own rule table, **every derived figure in this
sample is internally correct**. Re-computed by hand from the six sample rows:

| Check | Sheet states | Re-derived | Result |
|---|---|---|---|
| Total Sales Today (Σ col 3) | £22,493.05 | 22,493.05 | ✅ exact |
| Total Sales Yesterday (Σ col 4) | £21,971.65 | 21,971.65 | ✅ exact |
| Overall Growth | 2.37% | 521.40 ÷ 21,971.65 = 2.3730% | ✅ exact |
| Total Orders (Σ col 8) | 629 | 629 | ✅ exact |
| Yesterday Orders (Σ col 9) | 613 | 613 | ✅ exact |
| Order Growth | 2.61% | 16 ÷ 613 = 2.6101% | ✅ exact |
| Total Units Sold (Σ col 12) | 1,543 | 1,543 | ✅ exact |
| Average Order Value | £35.76 | 22,493.05 ÷ 629 = 35.7600 | ✅ exact |
| Per-row `Sales Diff` (6 rows) | — | 6/6 | ✅ exact |
| Per-row `Sales Growth %` (6 rows) | — | 6/6 | ✅ exact |
| Per-row `Order Growth %` (6 rows) | — | 6/6 | ✅ exact |
| Per-row `Avg Order Value` (6 rows) | — | 6/6 | ✅ exact |

**32 of 32 relationships reconcile.** The formula layer of the specification is therefore
**confirmed and needs no decision**. Only the *inputs* to those formulas are open.

⚠ Note: `Average Order Value` in the KPI panel is the **portfolio** AOV (Σ sales ÷ Σ orders), **not**
the mean of the per-account AOVs. The two differ whenever accounts have different order sizes; the
sample confirms the portfolio method.

## 🔴 Provenance warnings recorded at import

### 1. The file contains no business logic at all

Every cell that appears to hold a formula holds a **constant typed with a leading `=+`**:

| Cell | Actual stored value | What it is **not** |
|---|---|---|
| `E2` | the literal `=+435.3` | `=C2-D2` |
| `F2` | the literal `=+8.73%` | `=E2/D2` |
| `J2` | the literal `=+8.82%` | `=(H2-I2)/I2` |
| `B17` | the literal `=+2.37%` | any reference |

Nothing in the workbook references anything else. **There is no rule table** — the equivalent of
REQ-16's canonical rows 20–32 does not exist here.

**Consequence:** 100% of the report's logic must be **inherited from a governed project** or **raised
as a decision**. None of it can be read out of the spreadsheet. Inferring rules from six sample rows
would produce a plausible, fully-populated, silently-wrong report.

### 2. The sample data is fabricated — no figure may be reused

- The KPI panel states **`Total Accounts = 6`**, but only **two distinct account names** appear:
  `LEDSONE UK` (rows 2, 6, 7) and `ELECTRICALSONE UK` (rows 3, 4, 5). The sample is therefore
  **self-inconsistent on scope** and cannot be used to define which accounts are in scope.
- `Active Listing` reads **1212 · 12 · 2222 · 22 · 111** (blank on row 6) — keyboard filler, not
  measurements.
- Product names are generic (`LED Flood Light 100W`, `LED Ceiling Light`, `Solar Wall Light`,
  `LED Batten Light`, `Garden Spike Light`, `Under Cabinet Light`).
- Every row carries the same date, `2026-07-23` — the day the file was supplied.

### 3. Four columns are blank on every row, yet their trend columns are populated

`AH Listing` (16), `AH Listing Sales` (17), `PH Listing` (19) and `PH Listing Sales` (20) are
**blank on all six rows**. But `AH Sales Trend` (18) and `PH Sales Trend` (21) **are** populated —
and carry **exactly the same value as `Account Sales Trend` (22) on all six rows**:

| Row | col 18 | col 21 | col 22 |
|---|---|---|---|
| 2 | 📈 Up | 📈 Up | 📈 Up |
| 3 | 📉 Down | 📉 Down | 📉 Down |
| 4 | 📈 Up | 📈 Up | 📈 Up |
| 5 | 📈 Up | 📈 Up | 📈 Up |
| 6 | 📉 Down | 📉 Down | 📉 Down |
| 7 | ➡ Stable | ➡ Stable | ➡ Stable |

**The trend values were copied across.** They reveal nothing about how an AH or PH trend would be
computed. **Six of the 22 columns therefore have no definition and no source** — recorded as
decision **A** in `PROJECT_HOME.md`, and unanswerable by any database work.

### 4. The specification defines three things it never quantifies

- **Trend bands.** `📈 Up` / `➡ Stable` / `📉 Down` appear with no thresholds stated anywhere. The
  sample brackets them — `Up` at **+6.91%**, `Stable` at **+3.89%**, `Down` at **−8.20%** — so the
  cut lies between 3.89% and 6.91%, making **±5%** the candidate. The lower band is **unbracketed**
  (no sample value between 0% and −8.20%), so symmetry is assumed, not evidenced. Decision **E**.
- **The anchor.** The column is literally `Today's Sales`, but "today" is a **partial day**.
  Decision **B**.
- **The last-year comparator.** `Same Day LY` does not say whether it means the same calendar date or
  the same weekday. The sample's anchor 2026-07-23 is a **Thursday**; 2025-07-23 is a **Wednesday**.
  Decision **C**.

### 5. The file never names a channel

Nothing in the workbook says eBay, Amazon or Shopify. The account labels `LEDSONE UK` and
`ELECTRICALSONE UK` resolve to eBay stores under REQ-13's Thinesh-confirmed map (`led_sone`,
`electricalsone`), and all five of this requester's prior requirements are eBay — but **that is an
inference**. Recorded as decision **G**; it is why the project name is channel-neutral.

### 6. There is no Marketplace column

REQ-13 was corrected specifically because a single eBay store sells cross-border — `led_sone` sold to
UK, DE, FR, US and IT buyers within one month — so an account-only row attributes cross-border sales
to the store's home marketplace. The sample's `LEDSONE UK` appears to fold account and marketplace
into one label. Recorded as decision **F**.

---

The live data-availability audit
(`../../logs_or_screenshots/REQ-17_daily-sales-track/`) will be the authority for what can actually
be built. **It has not yet been run.** Until it is, nothing in this project has been proven against
live data.
