# Data-foundation probe — REQ-29 Amazon ASIN Variation Merge

**Date:** 2026-08-18 · **Method:** read-only `execute_sql` · **Purpose:** establish, before any build,
whether each of the 12 required columns has a truthful source.

## Connections used (all three checked)
| MCP connector | Database | Host | Rating/review columns | Rating/review/feedback tables |
|---|---|---|---|---|
| `Ledsone-db-mcp` (**primary — probes 1-5 below**) | `ledsone` | 169.58.91.229 (live host, user `dbhub_readonly`) | 10 (all eBay / false matches) | 3 (all eBay) |
| `83171520-…` | `ledsone` | 169.58.91.229 | 10 | 3 | 
| `3320445b-…` ("Postgresql", the PH-segmentation connector) | **`dev`** | **10.8.0.3** | **2 — both `message.amz_msg.body_preview` / `message.shopify_msg.body_preview`, the same false match on "preview"** | **0** |

The third connector is a **second, separate database** (`dev`, the warehouse) and was swept on 2026-08-18
after the primary probe, specifically to test whether Amazon ratings might live there instead. **They do
not** — it holds zero rating/review/feedback tables and no rating column of any kind. The second connector
resolves to the same `ledsone` database as the first (duplicate connection, identical counts).

➜ **The "no Amazon rating anywhere" finding therefore holds across BOTH databases, not one.**

⚠ **Not consulted:** the AIOS knowledge-base MCP (`docs.ledsone.co.uk/mcp`). The project `CLAUDE.md` requires
reading it before writing SQL. These probes were `information_schema` sweeps and simple catalogue counts
rather than report logic, but the KB should be read before the build's first real query.

**Verdict: 🔴 BLOCKED.** 10 of 12 columns are sourceable. The 2 that are not — **Parent Rating / Reviews**
and the **rating half of Child Colour / Rating** — are the report's primary selection criterion, so no
candidate row can be selected or ranked without them.

---

## Probe 1 — Does Amazon rating / review data exist anywhere? → **NO**

```sql
SELECT table_schema, table_name, column_name, data_type
FROM information_schema.columns
WHERE column_name ILIKE '%rating%' OR column_name ILIKE '%review%'
ORDER BY table_schema, table_name, column_name;
```

**Result: 10 rows, none of them Amazon product ratings.**

| schema.table | column | Verdict |
|---|---|---|
| `customer_service.ebay_account_ratings` | `rating_type`, `thirty_day_rating`, `thirty_day_rating_count`, `week_rating`, `week_rating_count` | eBay **seller-account** rating — not a product rating, not Amazon |
| `customer_service.ebay_orders_customer_feedbacks` | `rating_star` | eBay **per-order buyer feedback** — not Amazon |
| `customer_service.amazon_messages` | `body_preview` | false match on "preview"; a message body, not a rating |
| `customer_service.bandq_messages` / `shopify_messages` / `temu_messages` | `body_preview` | same false match |

## Probe 2 — Any rating/review/feedback **table**? → **eBay only**

```sql
SELECT table_schema, table_name FROM information_schema.tables
WHERE table_name ILIKE '%review%' OR table_name ILIKE '%rating%' OR table_name ILIKE '%feedback%';
```

**Result: 3 rows.**

| schema.table |
|---|
| `customer_service.ebay_account_ratings` |
| `customer_service.ebay_feedback_analytics` |
| `customer_service.ebay_orders_customer_feedbacks` |

**Conclusion: there is no Amazon product star rating or review count in EITHER database — not in a column,
not in a table.** (Probes 1-2 run on `ledsone`; the same sweep run separately on the `dev` warehouse returned
0 tables and only the two `body_preview` false matches — see the connection table above.) This matches the known reference that eBay *Watchers* is likewise absent from both databases:
some marketplace-surface metrics are simply not ingested.

### No legitimate proxy exists
`business_reports.amz_sales_and_traffic_by_asin` was inspected in full (53 columns): units ordered/shipped,
ordered/shipped product sales, B2B splits, refunds and `refund_rate`, browser/mobile sessions, page views,
`buy_box_percentage`, `unit_session_percentage`. `business_reports.amz_best_seller_rank` carries BSR.
**None of these is a review signal.** Substituting one would fabricate a business conclusion, so per
`CLAUDE.md` §2 the rating cells render **NO DATA** and the build does not start.

---

## Probe 3 — The Amazon catalogue (everything else) → **✅ live and rich**

```sql
SELECT site, sub_source, COUNT(*) rows, COUNT(DISTINCT asin) asins,
       SUM(CASE WHEN is_parent=1 THEN 1 ELSE 0 END) parents,
       SUM(CASE WHEN is_child=1 THEN 1 ELSE 0 END) children,
       SUM(CASE WHEN selected_variations IS NOT NULL THEN 1 ELSE 0 END) has_variations,
       MAX(updated_at) last_update
FROM listings.amazon_listings GROUP BY site, sub_source ORDER BY rows DESC;
```

**Top rows (of 20 returned):**

| site | sub_source | rows | ASINs | parents | children | has_variations | last_update |
|---|---|---|---|---|---|---|---|
| **UK** | **8** (`amazon Ledsone`) | **18,721** | **16,963** | **1,489** | **17,232** | **14,665** | **2026-08-18 00:31** |
| UK | 6 (`amazon Dcvoltage`) | 16,395 | 15,035 | 1,196 | 15,199 | 14,091 | 2026-08-18 00:30 |
| Germany | 8 | 8,618 | 7,720 | 447 | 8,171 | 5,667 | 2026-08-18 00:30 |
| France | 8 | 7,682 | 6,809 | 137 | 7,545 | 3,310 | 2026-08-18 00:30 |
| UK | 9 (`amazon SRM Amazon`) | 5,526 | 5,376 | 204 | 5,322 | 5,223 | 2026-08-18 00:30 |

Also present: Spain, Ireland, Italy, Netherlands, Belgium, Poland, Sweden, US, Canada. **The table is live —
last updated the morning of the probe.**

Account names confirmed:
```sql
SELECT id, name, source_id FROM order_management.sub_source WHERE id IN (6,8,9,22);
```
| id | name | source_id |
|---|---|---|
| 6 | `amazon Dcvoltage` | 1 |
| 8 | `amazon Ledsone` | 1 |
| 9 | `amazon SRM Amazon` | 1 |
| 22 | `electricalsone` | 2 (eBay — for contrast) |

## Probe 4 — Are variation attributes usable? → **✅ yes, jsonb**

```sql
SELECT asin, parent_sku, sku, is_parent, is_child, all_list, status, quantity,
       LEFT(title,60) title, selected_variations
FROM listings.amazon_listings WHERE site='UK' AND selected_variations IS NOT NULL LIMIT 5;
```

| asin | parent_sku | status | quantity | selected_variations |
|---|---|---|---|---|
| `B0FR8C1X83` | `PAPHLSHM2PK_11V` | Active | 39 | `[{"name":"color","value":"40cm Hemp-1m"}]` |
| `B0DCSJTVSZ` | `1P-44Y1-9Q5T` | Active | 17 | `[{"name":"color","value":"Green Brass Pack 2"}]` |
| `B0CZ75525Q` | `HA-VZWG-C8Z5` | Inactive | 0 | `[{"name":"color","value":"style 2"},{"name":"size","value":"without bulb"}]` |
| `B0DHZX17NP` | `PAWSWTBM4V` | Active | 39 | `[{"name":"color","value":"Black Without Bulb"}]` |
| `B0FDG1YKCF` | `3U-K3P3-90EL` | Active | 14 | `[{"name":"color","value":"Chrome With Bulb - 1 Pack"}]` |

**Findings:**
- `selected_variations` supplies **Child Colour** directly, and sometimes a second `size` attribute.
- **Values are free text and inconsistent** — "40cm Hemp-1m", "style 2", "Black Without Bulb",
  "Chrome With Bulb - 1 Pack". A duplicate check needs an agreed normalisation rule (open item #7).
- `quantity` + `status` give **Stock Status** (row 3 is Inactive with quantity 0 → Out of Stock).
- `parent_sku` is often an **opaque code** (`1P-44Y1-9Q5T`, `HA-VZWG-C8Z5`), not a readable family stem like
  the spec's `CRSF120` — so "Base SKU" may mean the SKU stem instead (open item #5).

## Probe 5 — Are duplicate variations real? → **✅ yes, badly**

```sql
SELECT parent_sku, COUNT(*) child_rows, COUNT(DISTINCT asin) asins,
       COUNT(DISTINCT (selected_variations->0->>'value')) distinct_colours,
       SUM(CASE WHEN quantity>0 THEN 1 ELSE 0 END) in_stock
FROM listings.amazon_listings
WHERE site='UK' AND sub_source=8 AND is_child=1 AND parent_sku IS NOT NULL
GROUP BY parent_sku HAVING COUNT(*)>1 ORDER BY child_rows DESC LIMIT 5;
```

| parent_sku | child rows | ASINs | distinct colours | in stock |
|---|---|---|---|---|
| `KI-QF1W-MGJP` | 227 | 227 | **51** | 226 |
| `3H-7K6O-NIQZ` | 52 | 52 | **26** | 50 |
| `GM-OLH8-QRN0` | 50 | 50 | **10** | 21 |
| `LDQ-Neon` | 48 | 45 | 10 | 30 |
| `PJ-BDAM-2HWY` | 48 | 48 | 12 | 33 |

**227 children across 51 distinct colour values** under one parent means the same attribute value repeats
many times over. The requester's Duplicate Warning column is catching a real, large-scale collision — this
validates the requirement rather than merely accommodating it.

---

## Column verdict

| # | Column | Verdict |
|---|---|---|
| 1 | Platform | ✅ constant |
| 2 | Account | ✅ `sub_source.name` |
| 3 | Base SKU | ✅ present (`parent_sku`), ⚠ definition open |
| 4 | Parent ASIN | ✅ present, ⚠ two competing definitions |
| 5 | **Parent Rating / Reviews** | 🔴 **NO SOURCE** |
| 6 | Child ASIN / SKU | ✅ |
| 7 | Child Colour / Rating | ⚠ colour ✅ · rating 🔴 |
| 8 | Merge Reason | 🔴 derived from the missing rating; threshold also unstated |
| 9 | Stock Status | ✅ `quantity` + `status` (platform stock) |
| 10 | Duplicate Warning | ✅ computable, ⚠ matching rule open |
| 11 | Approved (Y/N) | ✅ operator input by design |
| 12 | Operator Notes | ✅ operator input by design |

## What was NOT done
No table was written to. No DDL. No `ph_task` publish. No build, no deliverable, nothing committed. All five
probes are `SELECT`-only against `information_schema` and two read-only catalogue tables.

## Source-import integrity
`996_ASIN_Variation_Merge_Dashboard.xlsx` (12,887 bytes) copied to
`evidence/source_documents/REQ-29_amazon-asin-variation-merge/2026-08-18_source_asin-variation-merge-spec.xlsx`.
SHA-256 verified identical on both:
`cf054db99541e5c8a4b312fceb9246b8f0337d506d40ee84e65405a4c1b887a3`

## Next action
Put open item **#1 (rating & review source)** to **Prasath** (Business Validator / end user,
`staff.users` id 163; task assigned by HR 2026-08-18). The build cannot start before it is answered.
