# SYSTEM_REFERENCE — eBay Price Checker (REQ-12)

Complete functional detail of what the system does. Derived from the source spreadsheet, the owner's
CONFIRMED BUSINESS RULE, Thinesh's Q1–Q8, and the live source audit (all 2026-07-16). Plain-markdown, for
a leader or a new engineer.

## 1. Purpose
An **exception report of mispriced eBay listings**. For each live eBay listing SKU it derives a target
price from the company's own Amazon (or website) price, compares it to the current eBay price, and
classifies the drift so a manager reads only the rows that need a decision — a listing priced **too low**
bleeds margin; **too high** it stops converting.

## 2. The target-price rule (authoritative — supersedes the spreadsheet)
1. Take the **eBay listing SKU** (normalised — see §6).
2. Look it up in the **approved Amazon source**. If found with a valid price →
   `target = amazon_price × 0.90`, `target_source = AMAZON`.
   - On a duplicate match (SKU listed several times / prices), take the **LOWEST** Amazon price (Thinesh Q1).
3. Else look it up in the **approved website source**. If found → `target = website_price × 1.10`,
   `target_source = WEBSITE_FALLBACK`.
4. Else `target_source = NONE`, `Status = DATA MISSING`.
5. `target_price = ROUND(target_raw, 2)` — 2dp. (Whole-pound rounding parked.)
- **Never** blend, average, compute-both-and-choose, or let website override a valid Amazon match. **Exact
  SKU only** — never an approximate/parent/similar SKU or unrelated ASIN.

## 3. Drift → Status → Priority → Action
- `Difference = Current eBay − Target`; `Difference % = Difference ÷ Target`.
- **Tolerance:** `±£0.50` when eBay price < £20, `±£1.00` at £20 and above (Thinesh Q4/Q5 — resolves the
  sheet's £15-vs-£20 self-contradiction).
- **Status:** within tolerance → `Normal` · above → `High Price` (too expensive) · below → `Low Price` (too
  cheap) · no target → `DATA MISSING`, split into **NO COMPARATOR** (eBay-only product) vs **BUNDLE**
  (components not all priced).
- **Priority** (Thinesh Q6 — by money at risk): High if `|Difference| ≥ £5`, Medium if `≥ £2`, else Low;
  `Unknown` when no target. ⚠ **The £5/£2 cutoffs are the developer's, not Thinesh's** — he gave a
  direction, not numbers.
- **Action:** Normal → No Action · High → Reduce eBay Price · Low → Increase eBay Price · DATA MISSING →
  Investigate SKU and source mapping.

## 4. Sources (ledsone DB, Ledsone-db-mcp, read-only, refreshed 2026-07-15)
| Role | Object | Filter |
|---|---|---|
| Current eBay price | `listings.ebay_listings` | `all_list=1`, `site IN ('UK','Germany')`, `price>0` — **price per variant row** |
| Approved Amazon price | `listings.amazon_listings` | `all_list=1`, `sub_source=8` ('amazon Ledsone'), same sites; **LOWEST** on duplicate |
| Approved website price | `listings.shopify_listings` | `all_list=1`, `sub_source=104` ('ledsone', UK) / `108` ('ledsone-de', DE) |
| SKU normalisation | `inventory.products`, `inventory.product_pk` | ENC → `sku_original`; pack-char → qty |
| Account names | `order_management.sub_source` | human-readable account label |

## 5. Grain, currency, scope
- **Grain:** one row per eBay listing SKU (`item_id` + `sku`). Because eBay stores a price per variant row,
  "the current eBay price" is a single number per SKU — the REQ-11 item-K multi-variant problem does not
  bite here.
- **Currency:** UK = £, Germany = €. **No FX applied** (Q7 said "same rules"; no rate given) — the £
  tolerances are applied as EUR on the German side. Do not sum money across currencies.
- **Scope:** **126,070** live listings = 130,336 UK+DE listing SKUs minus the 4,266 in the 3 accounts
  Thinesh did not name (`dctransformer`/UK 3,741, `bestbringer`/UK 508, `ledsonede`/UK 17).

## 6. SKU normalisation (AIOS `sku-format-rules.md` + `ebay-listing-sku-filter.md`)
Applied to every listing before matching:
1. **`all_list = 1`** on all four listing tables — returns only real listable SKUs (parent containers
   excluded). Mandatory.
2. **Amazon `_` suffix** — base inventory SKU is everything before the first `_` (marketplace
   differentiator; Amazon only).
3. **ENC codes** — a SKU starting `ENC` is a shortened combo; resolve to the real SKU via
   `inventory.products.sku_original`.
4. **`<char>PK` pack suffix** — the char before `PK` decodes to a pack quantity via
   `inventory.product_pk`; multiply component prices by it in bundle sums.
5. **Combos (`+`)** — split on `+`, price each component, sum (Thinesh Q2). Works only when **every**
   component is priced (≈11% of bundles).

## 7. Output columns
**The report (source sheet's exact 13):** ID · SKU · Product Image · Account · Website Price · Amazon
Price · Target eBay Price · Current eBay Price · Difference · Difference (%) · Status · Priority · Action.
**The rule's 16-field audit trail** (in the UI xlsx build, and the dashboard's per-row detail):
`ebay_item_id · ebay_sku · amazon_match_status · amazon_sku · amazon_price · amazon_currency ·
website_match_status · website_sku · website_price · website_currency · target_source · target_price_raw ·
target_price · calculation_rule · source_updated_at · data_quality_note`. ⚠ `website_currency` is
**derived** (Shopify's currency column is empty) — GBP for sub_source 104, EUR for 108.

## 8. The 13 accounts (Thinesh's labels → DB accounts)
| Thinesh label | DB account (`sub_source`) | site | rows |
|---|---|---|---|
| LEDSone UK | led_sone (1) | UK | 30,866 |
| LEDSone UK Reg DE | led_sone (1) | Germany | 21,820 |
| Electricalsone UK | electricalsone (22) | UK | 15,571 |
| Sunsone UK | **so_926407 (4) — inferred** | UK | 12,110 |
| ElectricalSone DE | electricalsone (22) | Germany | 7,839 |
| Ledsone DE Reg DE | ledsonede (27) | Germany | 7,232 |
| Coventrylight UK | coventrylights (24) | UK | 6,478 |
| HUETTEN LAMP DE | huettenlampen (28) | Germany | 5,841 |
| Vintageinterior UK | vintageinterior (41) | UK | 5,479 |
| Retro LED UK | **re6865 (2) — inferred** | UK | 4,681 |
| Sunsone DE | **so_926407 (4) — inferred** | Germany | 3,406 |
| Lightingsone UK | lighting_sone (23) | UK | 3,067 |
| Homin DE | homin_gmbh (222) | Germany | 1,680 |

⚠ **Sunsone and Retro LED are inferred** — the only accounts that fit the UK/DE split, and the counts
reconcile exactly to 126,070, but the DB has no literal "sunsone"/"retro" string. Confirm with Thinesh.
Same seller can appear twice by marketplace (LEDSone UK vs LEDSone UK Reg DE = `led_sone` on the UK vs
German site).

## 9. Results (delivered 2026-07-16, all 126,070 rows)
Priced OK **21,138** · Too high **40,261** · Too low **22,008** · DATA MISSING **42,663**
(NO COMPARATOR 21,048 + BUNDLE 21,615). Only ~30% of rows with a target come out Normal — the rule is
well-centred (median drift from target +0.98%), so the flag rate is genuine price dispersion (±10%) vs a
tight ±5% tolerance, **not** a basis error.

## 10. ⚠ Known limitations (the report is correct-but-unsigned)
- **Shipping-blind** — item-price only; AIOS KB warns this misreports correctly-priced listings; shipping
  source not identified. **Rank, do not reprice.** The defining open item.
- **Sunsone / Retro LED** account identities are inferred.
- **Amazon ×0.90 = base ×1.08** vs the documented eBay target base ×1.10 (~2% gap).
- **Priority cutoffs** £5/£2 are developer defaults.
- **Q8** two new status values not yet in the production catalog (Sajeesan).
- **FX** undefined for the EUR accounts.
- **Bundles:** the sum-of-components rule recovers only ~11% of bundles (components often unpriced too).
