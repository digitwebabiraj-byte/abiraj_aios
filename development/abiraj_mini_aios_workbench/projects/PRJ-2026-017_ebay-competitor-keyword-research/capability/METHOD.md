# REQ-20 — Reusable Method: eBay Competitor & Keyword Research

**Owner:** Jarsini · **Built:** 2026-07-30 · **Type:** live eBay scrape + AI keyword generation
(NOT an internal-SQL report — see `../evidence/DATA_SOURCE_ANALYSIS.md`).

## Locked rules (signed off by Abiraj 2026-07-30)

1. **Site:** eBay UK (`ebay.co.uk`), UK-located items (`LH_PrefLoc=1`), sort by best/sold.
2. **Own-account filter (mandatory):** exclude our 13 eBay seller accounts, or "competitors" = us.
   In the Cone POC, **52 of 64 listings were ours**. Exclude:
   `led_sone, re6865, bestbringer, so_926407, dctransformer, electricalsone, lighting_sone,
   coventrylights, ledsonede, huettenlampen, vintageinterior, homin_gmbh, neighbourmarket`.
3. **Depth:** Top **5** genuine, relevant competitors per product category.
4. **Shipping column:** record **"Free postage"** vs **"With postage"** only (NOT the £ amount) —
   exact postage depends on the browser's delivery country and is unreliable; free-vs-paid is not.
5. **Sold Quantity:** exact value only when eBay displays "X sold"; otherwise blank (eBay limitation).
6. **Brand:** parsed from the eBay listing's **item specifics** ("Brand: …"); requires opening
   each listing. "Unbranded"/"NA" recorded as-is.
7. **Keywords (Primary/Secondary/Long-Tail):** generated per product from the product name/type.

## Product categories in scope (9)

Metal Shade Pendant Light (relabeled from "Cone" 2026-07-30, per Jarsini) · Wall Light · Metal shade Ceiling Light · Glass shade ceiling light ·
Spider Light · Cage pendant light · Pipe Light · Bulbs · Lamp Holder.

## Output

14-column sheet matching the brief:
Product Name · SKU · Competitor ID · Brand · Title · Sold Quantity · Price · Feedback Rate ·
Shipping type · Promotion Type & % · Primary Keywords · Secondary Keywords · Long-Tail Keywords · Notes.
File: `../evidence/final_outputs/REQ-20_.../REQ-20-D01_ebay_competitor_keyword.xlsx`.
