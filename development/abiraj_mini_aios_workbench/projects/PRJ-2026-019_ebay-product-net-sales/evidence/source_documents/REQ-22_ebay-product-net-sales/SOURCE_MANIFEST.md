# SOURCE MANIFEST — REQ-22 eBay Product Net Sales

COPY-only import. The original in Downloads is untouched; this is a byte-identical copy.

| Field | Value |
|---|---|
| File | `Kobiga task.xlsx` |
| Sheet | `Kobiga - Ebay Product net sales` (one sheet) |
| SHA-256 | `88a5af78c047133dfec4001a36f1923a946f419a1cac0f4fbc87f733f88cd30f` |
| Imported | 2026-08-03 |
| Origin | `C:\Users\digit\Downloads\Kobiga task.xlsx` (Kobiga) |

## What is canonical in this source
- **The 12 column headers are canonical** for shape and order:
  Order ID · SKU · Account · Gross Sales · VAT (20%) · Promotion % · Final Value Fee · Product Cost ·
  Postage · PPC Cost · General · Net Sales (NNV). *(The sheet spells "General" as "Gentral" in the
  header row — a typo; the intended label is **General**.)*
- **The Net Sales formula is canonical (business intent):**
  `Net Sales (NNV) = Gross Sales − VAT − Promotion − Final Value Fee − Product Cost − Postage − PPC Cost − General`,
  over **last-30-days** order data, with a **Net Sales Lookup** tab for a single Order ID.

## What is NOT canonical
- **The single sample row is illustrative, not a reconciliation baseline.** Order `02-14934-76138` shows
  Gross `26.38`, VAT `0.67`, Promotion `0.40`, Net `22.39`; the ≈`2.92` gap is un-itemised, so the exact
  deduction set, signs, `Promotion %`-vs-amount, and the `General` bucket **must be confirmed with Kobiga**
  and never inferred from this one row.
- **Product Cost is shown as a column but has no known source** in any database (see `SYSTEM_REFERENCE.md`).

## Notes
- Two duplicate Gross figures appear in the sample (`26.38` and `28.89`) with no label distinguishing
  them — clarify with Kobiga (gross vs gross-incl-postage?) during discovery.
