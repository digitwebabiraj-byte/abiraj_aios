# Thinesh's decisions — Q1–Q8 (2026-07-16)

Captured from chat. These answer the decision sheet
(`evidence/final_outputs/REQ-12_.../2026-07-16_abiraj_REQ-epc_REQ-12-D01_decision-sheet-thinesh.md`).
Where Thinesh **overruled** the recommended default, it is noted — several did.

| Q | Question | Thinesh's answer | Applied as |
|---|---|---|---|
| **Q1** | Multiple Amazon prices for one SKU | **Use the LOWEST Amazon price** (overruled "nominate one account") | `min(amazon_price)` on a duplicate match; duplicate no longer routed to DATA MISSING |
| **Q2** | Bundle/kit target | **Add up the component prices, then apply the normal rule** (overruled "exclude bundles") | `Σ(component price × pack qty) × 0.90` (Amazon) or `× 1.10` (website); works ~11% of bundles |
| **Q3** | Which Amazon account is "approved" | **amazon Ledsone only (sub_source 8)** | Amazon source scoped to `sub_source=8` |
| **Q4** | £15 or £20 tolerance threshold | **£20 — the band table** | Threshold = £20 |
| **Q5** | Accept the flag rate or widen tolerance | **Keep ±£0.50 / ±£1.00 and accept** (wrote "80%") | Tolerance unchanged |
| **Q6** | Priority rule | **By money at risk (bigger £ gap = higher)** | Priority banded on `ABS(Difference)`. ⚠ **cutoffs £5 / £2 are the developer's, not Thinesh's** — he gave a direction, not numbers |
| **Q7** | German accounts + what is SUNSONE | **"Apply the same UK rules and verify them against Ledsone Germany and the German website"** | Germany added (eBay DE vs Amazon DE sub_source 8 vs Shopify ledsone-de 108), all EUR. ⚠ **No FX rule given; SUNSONE not identified** |
| **Q8** | Status wording vs existing vocabulary | **Map onto the existing 8, add "too expensive" as a new value** | Report uses the existing labels; the two NEW values are **not** yet added to `staging_ai.pricing_safe_status_reason_catalog_v1` — that needs **Sajeesan** |

## Account names (Thinesh, 2026-07-16) — 13 account+region labels
7 UK: LEDSone UK · Electricalsone UK · Sunsone UK · Vintageinterior UK · Coventrylight UK · Lightingsone
UK · Retro LED UK.
6 DE: HUETTEN LAMP DE · Ledsone DE Reg DE · Homin DE · LEDSone UK Reg DE · ElectricalSone DE · Sunsone DE.

Mapped to DB accounts (see `SYSTEM_REFERENCE.md`). ⚠ **Two are inferred, not confirmed by Thinesh:**
`Sunsone = so_926407` and `Retro LED = re6865` (they are the only accounts that fit the UK/DE split and
the row counts reconcile exactly, but the DB has no literal "sunsone"/"retro" string).

## Still open after Q1–Q8 (route back to Thinesh / Sajeesan)
- **Shipping basis** — the AIOS knowledge base states a price check without shipping *"will misreport
  correctly-priced listings as violations"* and the shipping source is **not yet identified**
  (`amazon_listings.shipping_id`, an undocumented FK). ⇒ Status is **shipping-blind**.
- **FX rule** for the German (EUR) accounts — Q7 said "same rules"; the £ tolerances are applied as EUR.
- **SUNSONE UK / SUNSONE DE** identity — do not exist under those names.
- **Priority cutoffs** (£5 / £2) — developer defaults, need Thinesh's numbers.
- **Q8 two new status values** — need Sajeesan before they go into the production catalog.
