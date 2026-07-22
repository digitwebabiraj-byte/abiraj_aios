# Source Manifest — REQ-16 eBay Slow Moving & No Moving Products

**Project:** PRJ-2026-014_ebay-slow-no-moving-products
**Task:** REQ-16_ebay-slow-no-moving-products
**Imported:** 2026-07-22
**Import method:** COPY only — original left untouched in `C:\Users\digit\Downloads\`

## Files

| File | Bytes | SHA-256 | Role |
|---|---|---|---|
| `Thinesh task (3).xlsx` | 52,871 | `045ED710EC703AB11DC4754335E972F8C2A8222A5E9EB7E01BAD89EBA230CBD9` | Single-sheet specification: 20-column output shape (rows 1–11) + the 12-rule action engine (rows 20–32) |

Sheet name: `Slow Moving No moving Products ` — **note the trailing space**, which must be handled
when reading the file programmatically.

## Canonical-source ruling

There is only one file, and it has two parts that carry **different authority**:

- **Rows 20–32 (the rule table) are CANONICAL** for business logic. They define, verbatim,
  12 rules as `Condition → Action → Priority`.
- **Rows 1–11 (the sample listings) are ILLUSTRATIVE ONLY.** They define the required column
  order and header text, and nothing else.

## 🔴 Provenance warnings recorded at import

### 1. The sample data is fabricated — no figure may be reused

Rows 2–11 hold 11 invented listings. The item IDs are sequential placeholders
(`387654321001`–`387654321005`, `487654321001`–`487654321005`), the SKUs are synthetic
(`LED-001`…`SUN-005`), and the figures are round. **No number in the sample traces to any live
record.** They must never be used as a reconciliation baseline, a test expectation, or a sanity
check on live output.

### 2. The sample `Action Required` values are NOT rule-derived

Several sample rows carry an action their own stated conditions would not produce under the rule
table in the same file:

| Row | Figures | Rule that actually matches | Sample says |
|---|---|---|---|
| `LED-004` | 7d=1, 30d=3, 90d=9, stock=480, trend −81% | **Rule 4** → "Review Competitor Pricing" | "Bundle Product" |
| `SUN-001` | 7d=0, 30d=1, 90d=6, trend −82% | **Rule 3** → "Reduce Price by 5–10%" | "Price Review" |
| `SUN-003` | 7d=1, 30d=5, 90d=13, trend −75% | no rule → Monitor | "Increase PPC" |

The sample labels are also **abbreviated** versions of the rule table's action text
("Run Promotion" vs "Run Clearance Promotion"; "Delist" vs "End Listing / Clear Stock").

**Consequence:** the sample cannot be used to infer rule precedence, and the action strings in the
deliverable must come from **rows 20–32**, not from the sample column.

### 3. The sample account labels do not match the live account roster

The sample shows three accounts — `LEDSone UK`, `SunSone UK`, `ElectricalSone UK`. Live, these
resolve to `led_sone`, `so_926407` and `electricalsone`. The sample also mislabels row 8
(`SUN-002`, a `SUN-` SKU) as belonging to `ElectricalSone UK`, which is internally inconsistent.

The owner has since scoped the build to **all** active eBay accounts on UK + Germany
(12 accounts), superseding the three-account impression the sample gives.

### 4. The specification defines two things it never quantifies

- **Rule precedence.** Priorities are assigned (Critical/High/Medium/Low) but the file never states
  how a listing matching several rules resolves.
- **Rule 8's "PPC Spend High."** No threshold is given anywhere in the file.

Both are recorded as explicit assumptions in `PROJECT_HOME.md` (Decisions **C** and **G**) and must
be confirmed by the Business Validator.

---

The live data-availability audit
(`../../logs_or_screenshots/REQ-16_ebay-slow-no-moving-products/2026-07-22_data_availability_audit.md`)
is the authority for what can actually be built; it supersedes every impression given by the
fabricated sample.
