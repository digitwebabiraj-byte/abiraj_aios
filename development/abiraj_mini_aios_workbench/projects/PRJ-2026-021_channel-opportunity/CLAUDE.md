# CLAUDE.md — PRJ-2026-021 Channel Opportunity

Project execution rules. Inherits the workbench `CLAUDE.md`; the rules below are additional.

## Identity
- Project `PRJ-2026-021_channel-opportunity` · code `chop` · Task `REQ-24`.
  Owner Abiraj; Business Validator **Mahima**. **IDs provisional** (source is a spec mock-up, no
  requirement number; REQ-23 is taken by `fmp`). A new day/session does not mint a new Task ID.

## 1. The source workbook is a layout spec, not data
Every value in `mahima task.xlsx` (`xyz`, `dgh`, `kytd`, 100 / 5 / 2 …) is an **illustrative sample**.
It defines the desired **columns, the Opportunity classes and the Action vocabulary** only. Never copy a
sample number into a deliverable. Every delivered figure must trace to live `ledsone` / warehouse data.

## 2. Confirm the business rules before building — do NOT invent thresholds
**Opportunity** (Shopify winner / Marketplace winner / Missing channel) and **Action** are business rules,
not raw columns. "Selling well in one channel", "weak in another" and "missing" are numeric judgements — the
sales metric (units vs revenue), the window, and the thresholds that separate winner / weak / missing must
all be confirmed with Mahima. A three-row mock-up is not a spec.

## 3. This is a cross-channel comparison keyed on the base SKU
The whole point is one row per **product**, sales spread across Shopify / Amazon / eBay. The same physical
product carries a different Product ID per channel (ASIN / eBay Listing ID / Shopify id) but a shared base
SKU — the pivot key must be the **clean base SKU**, never a per-channel Product ID (the FMP combined-table
rule). Resolve the clean SKU before pivoting.

## 4. Per-channel isolation + eBay grain
- Amazon = `which_channel=1`, eBay = `which_channel=2`, Shopify = `which_channel=3`. Pull each channel's
  sales separately, then pivot per base SKU.
- **eBay: never join sales by SKU alone** — one SKU → many item_ids (~13× overstatement). Attribute by
  order_id / item_id; isolate eBay with `source_id=2`.

## 5. Currency — confirm the scope before summing money
If the sales metric is **revenue**, `orders.total` / money fields are in each marketplace's own currency
and there is no FX table (the DST currency trap). Confirm the market scope (the fmp sibling is DE/€) and
never blend currencies or mislabel a symbol. If the metric is **units**, this is moot — prefer units unless
Mahima asks for revenue.

## 6. "Missing channel" means a real zero, proven by absence
A Missing-channel opportunity is a SKU that sells in ≥1 channel and has **no** sales (and ideally no live
listing) in another. Detect it with a LEFT JOIN / absence check, not by assuming. A `0` is written only
where the true value is zero; an unresolvable value renders `NO DATA`, never a guess.

## 7. Source of record + read the KB first
- This is **multi-domain** (Orders across 3 channels; optionally Listings to prove "no listing") →
  use `text-to-sql-multi` (+ `ppc-stock-lookup` only if stock is added later).
- Prefer **raw `ledsone`** for eBay (the warehouse hides SMART campaigns / is thinner).
- **Read the AIOS knowledge base (`docs.ledsone.co.uk/mcp`) before writing any SQL** — skipping it caused
  wrong builds twice. Apply `all_list=1`, VARCHAR casts, the parent-row title trap.

## 8. Read-only; never fabricate
- READ-ONLY on all source tables. No INSERT/UPDATE/DELETE/DDL. The only future write is a guarded
  `ph_task` publish on explicit owner instruction after the audience is named and each recipient verified.
- Every filled column traces to a real `schema.table.column`. Unsourceable columns render `NO DATA`.
- Credentials come from the git-ignored shared store, never committed.

## 9. One generator module
The report (and any future scheduled run) comes from a single module `sql/REQ-24_.../chop_build_d01.py`.
Do not fork a second fetch path.

## 10. Stop conditions (in addition to the workbench's)
- A build is requested before the sales metric, window, market scope, the numeric winner/weak/missing
  thresholds and the Action vocabulary are confirmed with Mahima.
- A build would populate Opportunity / Action by guessing a rule or threshold.
- A publish is requested before the audience is named and each recipient verified.
- Any request to blend currencies when the metric is revenue.

## Vocabulary
Channel Opportunity = per-SKU cross-channel sales gap · Shopify winner / Marketplace winner / Missing
channel = the Opportunity classes · which_channel 1/2/3 = Amazon/eBay/Shopify · base SKU = the clean
cross-channel roll-up key · NO DATA = no truthful source.
