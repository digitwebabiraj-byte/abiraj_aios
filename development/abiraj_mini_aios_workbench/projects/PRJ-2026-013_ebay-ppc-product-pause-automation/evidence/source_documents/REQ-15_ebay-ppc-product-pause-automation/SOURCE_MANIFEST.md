# Source Manifest — REQ-15 eBay PPC Product Pause Automation

**Project:** PRJ-2026-013_ebay-ppc-product-pause-automation
**Task:** REQ-15_ebay-ppc-product-pause-automation
**Imported:** 2026-07-21
**Import method:** COPY only — originals left untouched in `C:\Users\digit\Downloads\`

## Files

| File | Bytes | SHA-256 | Role |
|---|---|---|---|
| `eBay PPC Product Pause Automation V1.xlsx` | 31,952 | `AE218EE09C67EE8B60332A749805F3422CD66203C45CE267A7D24AE0EEF90D95` | 5-sheet planning workbook (Dashboard, Pause Log, Input Data, Pause Rules, Custom Rules) |
| `eBay PPC Product Pause Automation V1.html` | 58,113 | `FEF3EA59CC6708ED27D0B2F7054E949099E264002C24D6B7525FCAC97723BFE0` | Self-contained interactive console — **carries the canonical rule engine** in its `evaluate()` function |

## Canonical-source ruling

The two files describe **one** system. Where they differ, **the HTML is canonical** for business logic:

- The HTML holds the executable rule engine (`evaluate()`), the ordered gates, the rescue clauses
  and the per-row decision traces.
- The xlsx `Pause Log` is a rendering of the same decisions; its `Custom Rules` sheet explicitly
  states it is "a planning worksheet (not wired into the Pause Log formulas)".
- The xlsx `Pause Rules` sheet and the HTML `ACOS_UK` constant agree on all five thresholds.

## ✅ VERIFIED REAL — 2026-07-21 (supersedes an earlier wrong finding)

**The sheet's data is genuine, live, campaign-grain data.** Reconciled against
`ebay_campaigns.performance_data` for the stated 01–07 Jul 2026 window:

| Campaign | Sheet spend | DB spend | Sheet clicks | DB clicks |
|---|---|---|---|---|
| JD \| MH \| LEDSONE Cable \| Manual | 13.93 | **13.93** | 81 | **81** |
| JD \| MH \| Wall lights \| Shimee \| Manual | 10.45 | **10.45** | 57 | **57** |
| JD \| Cables \| Video \| Manual | 7.67 | **7.67** | 39 | **39** |
| JD \| PH \| Lampshade \| Utharsika \| Manual | 40.28 | 40.34 | 249 | 250 |
| JD \| Wall lights \| New \| Manual | 31.91 | 31.69 | 197 | **197** |
| JD \| Target Mixed \| New \| ST \| smart | 42.77 | 42.92 | 201 | **201** |

Campaign names match exactly (including the double space in
`JD | PH | Lampshade  | Utharsika | Manual`), and `Type` matches live `campaign_target_type`.

> 🔴 **CORRECTION.** An earlier check in this project concluded the sheet's IDs "exist nowhere" and
> that its rows were placeholders. **That was wrong.** The `Item ID / SKU` column holds
> **campaign IDs**, not item IDs — e.g. `164113429012` is the campaign
> `JD | Target Mixed | New | ST | smart`. They were looked up in `listings.ebay_listings` (the wrong
> table) and their absence was over-interpreted. **The sheet is real.** Lesson: confirm what an ID
> column actually is before concluding data is fabricated.

Minor variances that are expected, not defects: `orders` and therefore `ACOS` differ on some rows
(e.g. 23 vs 14) because attributed-sales figures are restated as eBay's attribution window matures
after the export was taken. Spend and clicks — the immutable figures — match.

## Provenance warnings recorded at import

1. **The sample data is one 7-day export.** The HTML's own header comment states the source was a
   single eBay Promoted Listings campaign report for 01–07 Jul 2026, that `acosWin` (30D) and
   `acos7` are both set to that one 7-day ACOS, and that the 14D fields reuse the same 7-day
   figures. Consequence: **Rule 1's improving-trend rescue can never fire in the sample**
   (no value is simultaneously >=40% and <20%).
2. **Stock and price are not in that export.** The same comment says item ID / SKU / price / stock
   are unavailable and should render as "—". `price` is indeed `0` for all 42 rows — but `stock`
   carries specific values (142, 3, 0, …) that drive 8 of the 16 sample pauses. **Those stock
   figures have no traceable source in the eBay export** and must not be treated as real.
3. The sample is campaign-grain, not listing-grain: `sku` is `"—"` for all 42 rows.

These are properties of the mockup, not defects to reproduce. The live-data audit
(`../../logs_or_screenshots/REQ-15_.../2026-07-21_step2_data_availability_audit.md`) supersedes
all three for the real build.
