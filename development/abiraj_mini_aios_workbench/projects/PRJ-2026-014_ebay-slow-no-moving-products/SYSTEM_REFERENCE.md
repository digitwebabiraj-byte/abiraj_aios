# SYSTEM_REFERENCE — eBay Slow Moving & No Moving Products (ESNM)

Complete functional detail of what this system does, for a leader or a new engineer. Derived from
the canonical source (`Thinesh task (3).xlsx`, rule table rows 20–32) and the live audit of
2026-07-22.

| | |
|---|---|
| Project | `PRJ-2026-014_ebay-slow-no-moving-products` · code `esnm` |
| Task | `REQ-16_ebay-slow-no-moving-products` |
| Deliverables | **D01** report (built) · **D02** HTML dashboard (not started) · **D03** scheduled refresh (not started) |

---

## 1. Purpose

For every sellable eBay listing across the LEDSone group's accounts on **UK and Germany**, decide
whether it is moving, slowing or dead, and state **one recommended action** — derived from its sales
over three windows, its year-on-year change, its stock, its traffic and its ad spend.

The system **recommends only**. Applying an action stays a human step in Seller Hub.

---

## 2. Rule engine — the ordered gates

Twelve rules, verbatim from the source. Evaluated in **priority order — Critical → High → Medium →
Low — first match wins**; within one priority band the lower rule number wins.

**Evaluation order: 1 → 2 → 3 → 4 → 5 → 7 → 8 → 9 → 10 → 11 → 12.** Rule 6 is omitted entirely.

### Critical
**Rule 1** — `90-day sales = 0` → **End Listing / Clear Stock**
The dead-stock gate. Claims 8,067 of 11,156 listings (72.3%).

### High
**Rule 2** — `30-day sales = 0 AND stock > 50` → **Run Clearance Promotion**
Still sold in the last 90 days, but stalled with material stock behind it.

**Rule 3** — `7d = 0 AND 30d ≤ 2 AND 90d ≤ 5` → **Reduce Price by 5–10%**
Trickling, not dead. A price nudge is the cheapest intervention.

**Rule 4** — `sales dropped > 80% vs the same 90-day window last year` → **Review Competitor Pricing**
Only evaluated where last year's sales were > 0 (the ratio is undefined otherwise).

**Rule 5** — `views > 100 AND conversion rate < 1%` → **Improve Images & SEO Title**
Traffic arrives but does not convert — a listing-quality problem, not a demand problem.
⚠ Only evaluated where a traffic row exists (§5.2).

**Rule 7** — `stock > 100 AND 90-day sales < 5` → **Bundle with Best Seller**
Deep stock against negligible movement.

**Rule 8** — `PPC spend > £5.00 over 30 days AND 30-day sales = 0` → **Pause PPC Campaign**
⚠ The £5.00 floor is an **assumption** — the source says "high" and never defines it.
⚠ EPPA (`PRJ-2026-013`) remains canonical for pause decisions; this is a coarse flag only.

### Medium
**Rule 9** — `views < 50 in 30 days` → **Improve SEO & Increase Promotion**
⚠ Only evaluated where a traffic row exists (§5.2).

**Rule 10** — `listing age > 180 days AND last sale > 90 days ago` → **Refresh or Relist**
🔴 **Structurally unreachable.** Any listing meeting this necessarily has zero 90-day sales, so
Rule 1 claims it first. Matched **0 of 11,156**. See decision C.

**Rule 6** — `watchers > 10 AND no 30-day sales` → *Send Offer / Discount*
🔴 **Cannot be evaluated — `Watchers` has no source in either database.** Never fires.

### Low
**Rule 11** — `30-day sales ≥ 10` → **Maintain Current Strategy**
**Rule 12** — `7-day sales > previous 7-day sales AND > 0` → **Increase Stock & PPC Budget**

### Fallback
No rule matched → **Monitor — No Rule Matched** (171 listings).

---

## 3. Thresholds — configuration, never code

All live on the workbook's **Rules** sheet as editable yellow cells. `Action Required` (column T) is
a live formula referencing them, so changing one re-evaluates all 11,156 rows.

| Rule | Threshold(s) | Source |
|---|---|---|
| 1 | 90d ≤ **0** | source |
| 2 | 30d ≤ **0** · stock > **50** | source |
| 3 | 7d ≤ **0** · 30d ≤ **2** · 90d ≤ **5** | source |
| 4 | trend ≤ **−80%** | source |
| 5 | views > **100** · CVR < **1%** | source |
| 6 | watchers > **10** | source (unusable) |
| 7 | stock > **100** · 90d < **5** | source |
| 8 | spend > **£5.00 / 30d** | 🔴 **ASSUMED** |
| 9 | views < **50** | source |
| 10 | age > **180d** · idle > **90d** | source |
| 11 | 30d ≥ **10** | source |
| — | **precedence** | 🔴 **ASSUMED** |

---

## 4. Data model — live sources

### 4.1 Two databases are mandatory

| Domain | Database | Object |
|---|---|---|
| Listings | `ledsone` | `listings.ebay_listings` |
| Accounts | `ledsone` | `order_management.sub_source` (`source_id = 2`) |
| Sales | `ledsone` | `order_management.orders` + `order_item_info` |
| eBay PPC | `ledsone` | `ebay_campaigns.performance_data` |
| **Traffic** | **warehouse `order_management_copy`** | **`public.traffic_data` (`which_channel = 2`)** |

Neither database can build the report alone — see `CLAUDE.md` §2.

### 4.2 Windows (anchor **2026-07-22**, the last complete sales day)

| Window | Range |
|---|---|
| Last 7 days | 2026-07-16 → 2026-07-22 |
| Prior 7 days (Rule 12) | 2026-07-09 → 2026-07-15 |
| Last 30 days | 2026-06-23 → 2026-07-22 |
| Last 90 days | 2026-04-24 → 2026-07-22 |
| Same Period Last Year | 2025-04-24 → 2025-07-22 |

### 4.3 Sales counting

Units = `COALESCE(NULLIF(real_qty,'')::numeric, NULLIF(item_quantity,'')::numeric, 0)`, joined
`orders.id = order_item_info.order_id`, aggregated by `order_item_info.item_id`.

Order status: **`Cancelled` excluded** (61 in window); **`Refunded` (455) and `Inprogress` (118)
included** — both still evidence demand for a slow-moving assessment.

### 4.4 Scope filter

`sub_source.source_id = 2` · `ebay_listings.site IN ('UK','Germany')` · `is_ended = 0` ·
`is_child = 0` · `item_id` not null. **`wrong_sku` is deliberately NOT filtered** — see `CLAUDE.md` §5.

---

## 5. Known structural limits (audited 2026-07-22)

### 5.1 `Watchers` — no source anywhere
Both databases scanned for `watch`/`favorite`/`wishlist`/`saved`; only unrelated `staging_ai` hits.
eBay exposes it only via the Trading API, not ingested. Column 17 ships **blank**, never `0`.

### 5.2 Traffic lost 11 days
78 of 91 days present (7–11 May, 26 Jun, 29 Jun–1 Jul, 26 Apr, 18 Jul lost; 21–22 Jul is the normal
lag). eBay-specific — Shopify loaded fine on all of them. Root cause is in neither database.
Views understated ~12% over 90 days, **~23% over 30 days**. Rules 5 and 9 evaluated only where a
traffic row exists.

### 5.3 PPC — a trade-off, not a limit
`ledsone` = 65 days but **complete incl. SMART**; warehouse = 90 days but **omits SMART at ad grain**
(£31,481 ad vs £39,454 campaign). Built on `ledsone`; Rule 8 runs on 30 days, fully covered by both.

### 5.4 51.7% of listings carry `wrong_sku = 1`
5,767 of 11,156 — all real, sellable listings with proper titles, stock and prices. Their SKU string
is not a clean inventory code, so column 4 is unreliable for them and none bridge to inventory.

### 5.5 `ebay_listings.status` is ~99% NULL
Never read directly; Listing Status is derived from `is_ended`/`end_date`.

### 5.6 Days Since Last Sale for never-sold listings
Where a listing has never sold in the order history, the **listing's age** is shown instead so
Rule 10 still evaluates. Disclosed on the report.

---

## 6. Output — REQ-16-D01

Five sheets. Column order and header text are fixed by the source and reproduced exactly.

| Sheet | Contents |
|---|---|
| **Slow Moving No moving Products** | The 20 source columns · 11,156 rows · sorted Critical→Low · auto-filter · frozen header · priority-coloured Action cells |
| **Summary** | Volume by rule (with % of total) + breakdown across all 16 account × marketplace combinations |
| **Rules** | The 12 rules, actions, priorities and **editable yellow threshold cells**; Rule 6 greyed out with its reason in red |
| **Engine Inputs** | Prev-7-day sales · listing age · PPC spend · PPC attributed sales · traffic-present flag · matched rule · priority |
| **Data Notes** | Every source, assumption and gap — so a reader of the file alone cannot be misled |

**Live formulas:** column N (Sales Trend) `=(L−M)/M`, and column T (Action Required), a nested `IF`
implementing all eleven evaluable rules against the Rules and Engine Inputs sheets.

### The 20 columns
`Image · Account · Brand · SKU · Item ID · Product Title · Category · Current Price · Stock ·
Last 7 Days Sales · Last 30 Days Sales · Last 90 Days Sales · Same Period Last Year · Sales Trend ·
Days Since Last Sale · Views (30 Days) · Watchers · Conversion Rate · Listing Status ·
Action Required`

---

## 7. Baseline numbers — anchor 2026-07-22

| Priority | Rule | Action | Listings |
|---|---|---|---|
| Critical | 1 | End Listing / Clear Stock | **8,067** (72.3%) |
| High | 2 | Run Clearance Promotion | 1,210 |
| High | 3 | Reduce Price by 5–10% | 851 |
| High | 7 | Bundle with Best Seller | 149 |
| High | 4 | Review Competitor Pricing | 42 |
| High | 5 | Improve Images & SEO Title | 26 |
| High | 8 | Pause PPC Campaign | 2 |
| Medium | 9 | Improve SEO & Increase Promotion | 476 |
| Medium | 10 | Refresh or Relist | **0** (unreachable) |
| Medium | 6 | Send Offer / Discount | **0** (no data) |
| Low | 11 | Maintain Current Strategy | 109 |
| Low | 12 | Increase Stock & PPC Budget | 53 |
| — | — | Monitor — no rule matched | 171 |
| | | **Total** | **11,156** |

**Scope:** 12 accounts · 16 account × marketplace · UK 7,685 / Germany 3,471.

**Verification:** engine implemented twice independently (live Excel formulas + Python), diffed
**11,156/11,156 with 0 mismatches**; **0 formula errors** workbook-wide; item `164889807930`
reconciled exactly field-by-field against both databases.

⚠ These figures rest on two unconfirmed assumptions — **rule precedence** and **Rule 8's £5.00
threshold**. Precedence in particular is what makes 8,067 listings read "End Listing".
