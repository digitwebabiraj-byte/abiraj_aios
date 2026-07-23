# Data-availability audit — REQ-17 Daily Sales Track

**Executed:** 2026-07-23 · **Method:** read-only SQL via MCP against both live databases · **Writes:** none

**Verdict: 🟢 GREEN on feasibility · 🔴 RED on the inherited status filter.** The report is buildable
and the daily grain is sound, but REQ-13's `order_status='Completed'` filter **cannot be inherited
unchanged** — under the owner's confirmed D−1 anchor it understates yesterday by **63%**.

---

## 1. Connectivity — which MCP reaches what

| MCP | Database | Host:port | Connected as | Server TZ |
|---|---|---|---|---|
| `39dbecb8-…` | `order_management_copy` (warehouse) | 10.8.0.3 : **5435** | ⚠ **`postgres`** | **Asia/Colombo (+05:30)** |
| `Ledsone-db-mcp` | `ledsone` | 10.8.0.5 : **5432** | `dbhub_readonly` | **Europe/London** |

⚠ **Safety finding.** The warehouse MCP connects as **`postgres`**, not the restricted `temp_user`
that `AUTOMATION_PLAYBOOK.md` and every prior project assume. This connection has **full write
capability** on the warehouse. Read-only discipline is not enforced by the connection — only by the
operator. Every query in this audit was read-only.

**Both MCPs are required.** Neither database alone can build the report — see §6.

`postgres` (the separately-registered connector) is **not needed**; the `39dbecb8` MCP already
reaches that database. It is also unauthenticated in this session.

---

## 2. 🟢 The daily grain works

`public.order_transaction.order_date` is `timestamp without time zone`, and **every row carries a
real clock time** (checked across 13 consecutive days: `rows_with_clock_time` = `lines` on all 13).
There are no midnight-stub rows, so `order_date::date` buckets cleanly.

**The daily series has no gaps** across the observed window — 10 to 14 consecutive days present,
112–175 orders/day. This is materially better than REQ-16's experience, where the eBay *traffic*
feed had lost 11 of 91 days.

## 3. 🟢 Timezone — buckets are correct, but `CURRENT_DATE` is not safe

The two servers run in different timezones, which raised the risk that `::date` would bucket UK
trading days differently on each side. **Tested and cleared** by comparing the hour-of-day
distribution of eBay orders over the same 7 days:

| Hour | 03 | 05 | 09 | 13 | 17 | 20 | 23 |
|---|---|---|---|---|---|---|---|
| Warehouse | 9 | 10 | 71 | 73 | 82 | 75 | 24 |
| ledsone | 6 | 7 | 65 | 73 | 79 | 71 | 22 |

**Identical shape, no 5.5-hour shift** — a UK trading pattern (trough 03:00–05:00, peak
09:00–21:00) in both. ⇒ **`order_date` is stored in UK time in BOTH databases**, and the daily
buckets agree across them.

⚠ **But the anchor arithmetic must not use the warehouse's `CURRENT_DATE`.** It returns the
**Colombo** date, which rolls over 4.5 hours before London's — between 19:30 and 23:59 UK the
warehouse already believes it is tomorrow. Pin the anchor date explicitly in the build; do not
derive it from `CURRENT_DATE` on either server.

---

## 4. 🔴 THE HEADLINE — orders do not reach `Completed` on the day they are placed

This is the finding that changes the build.

Orders enter as `New` (warehouse) / `Inprogress` (ledsone) and transition to `Completed` roughly
**two days later**, presumably on dispatch. Measured on eBay orders, warehouse, 2026-07-23:

| Order day | `Completed` | Non-cancelled | % matured | Sales (`Completed`) | Sales (non-cancelled) |
|---|---|---|---|---|---|
| 23 Jul (today) | 0 | 5 | **0.0%** | — | £63.97 |
| **22 Jul (D−1)** | **37** | **141** | **26.2%** | **£1,102.43** | **£3,010.04** |
| 21 Jul (D−2) | 152 | 153 | **99.3%** | £2,884.11 | £2,884.11 |
| 20 Jul | 144 | 146 | 98.6% | £2,845.06 | £3,319.86 |
| 19 Jul | 174 | 174 | 100.0% | £3,783.17 | £3,783.17 |
| 18 Jul | 117 | 118 | 99.2% | £2,288.28 | £2,288.28 |
| 17 Jul | 131 | 132 | 99.2% | £2,701.82 | £2,701.82 |
| 16 Jul | 141 | 141 | 100.0% | £2,700.81 | £2,700.81 |
| 15 Jul | 133 | 134 | 99.3% | £3,263.79 | £3,263.79 |
| 14 Jul | 139 | 139 | 100.0% | £3,420.38 | £3,420.38 |

**Consequence.** The owner has confirmed (2026-07-23) that a report generated on run-date **R**
reports **R−1** as "Today" and **R−2** as "Yesterday". Under REQ-13's inherited
`order_status='Completed'` filter, the "Today" column would read **£1,102.43 / 37 orders** when the
true figure for that day is **£3,010.04 / 141 orders** — a **63% understatement**, presented next to
a fully-matured "Yesterday" column. **Every daily report would show a catastrophic one-day collapse
that did not happen.**

**⇒ The owner's confirmed D−1 anchor and REQ-13's `Completed`-only filter are incompatible.** One
must give. See decision **M** in `PROJECT_HOME.md`.

### Correction to an earlier reading

An initial pass concluded the warehouse feed "lags ~22 hours" (latest order 2026-07-22 12:33, zero
rows today). **That was an artefact of the `Completed` filter**, not a sync lag. The warehouse holds
23 July orders and is current; `Completed` orders simply stop ~2 days back. Cross-checked against
ledsone, which is live to within ~20 minutes: the two databases agree on order counts per day once
statuses are compared like-for-like (22 Jul: warehouse 141 non-cancelled, ledsone 143 total). **There
is no ingestion lag.**

⚠ Note the status vocabularies differ slightly between the databases — warehouse `New` (103) vs
ledsone `Inprogress` (105) for the same day. Do not assume the enums are identical.

---

## 5. 🟢 AH / PH — decision A is now half-answered

An earlier assessment recorded that no database work could answer decision **A**. **That was wrong
for the PH half.**

### PH = Product Holder — SOURCED, two independent ways

**(a) The live assignment — ledsone `staff` schema:**

| Table | Columns |
|---|---|
| `staff.ph_categories` | `id, category_name, user_id, assign_date, created_at` |
| `staff.ph_category_products` | `id, ph_category_id, ref_id, source_id, assign_date, is_updated` |
| `staff.users` | `id, first_name, last_name, email, username, branch, role, status` |

A product **category** is assigned to a staff **user**; products (`ref_id`) belong to a category per
`source_id`. **eBay (`source_id = 2`): 3,270 rows · 3,098 distinct refs · 50 categories.**

| Category | Staff | eBay products |
|---|---|---|
| Wall Lamps | shimee | 374 |
| Wire Cage | paulr | 322 |
| Bulbs | thuwaraga | 287 |
| Cable | Jasmini | 252 |
| Transformer | Dilani | 231 |
| Lampshade | utharsika | 182 |

⚠ **Coverage is partial: 3,098 of ~11,156 eBay listings ≈ 28%.** `PH Listing` will be blank for
roughly seven listings in ten.

⚠ `staff.users` **exists in ledsone**. REQ-16 recorded that `staff.users` does not exist — that was
true of the **warehouse** only. Both statements are correct for their own database; record which.

**(b) Already on the sales rows — warehouse `public.order_transaction` carries `user_id` and
`user_name`.** PH sales therefore need no join. ⬜ **One verification still outstanding:** confirm
that this `user_name` is the PH holder and not some other actor.

**(c) Also available:** warehouse `analytics.ph_segment` (`which_channel = 2`) — 88,530 rows /
**3,076 eBay refs** / 22 PHs, closely matching ledsone's 3,098. ⚠ **Stale — `max(period_end)` =
2026-07-14** (9 days old). It is a derived period report, not the assignment; prefer ledsone's
`staff.*` tables.

### AH = Account Holder — STILL UNSOURCED

- **ledsone: absent.** `staff.ph_categories.user_id` is the **only** user linkage in the entire
  database. `order_management.sub_source` (the account table) has **no** assigned-user column.
- **Warehouse: only unvalidated candidates** — `staging_ai.cppc_platform_staff_ownership_v1` and
  `staging_ai.cppc_campaign_responsibility_registry_v1` carry account + staff_name + role, but
  `staging_ai` is the schema REQ-11 established as **never promoted / VALIDATION_REQUIRED**, and both
  are advertising-scoped.

**⇒ Decision A narrows to the AH half only.**

---

## 6. Why both databases are required

| Only the warehouse has | Only ledsone has |
|---|---|
| `order_transaction.order_total` — **the inherited REQ-13 sales definition**. ledsone's `order_management.orders.total` is a *different column*; using it breaks the inheritance | `listings.ebay_listings.title` — **`Best Seller` names** |
| `order_transaction.user_id` / `user_name` — PH already on the sales line | `staff.ph_categories` + `ph_category_products` — **the live PH assignment** |
| `public.listing_data` — REQ-13's `Active Listing` definition | `staff.users` — staff roster |
| `analytics.ph_segment` — listing→PH (stale) | `listings.ebay_listings` — REQ-16's `Active Listing` definition, price, stock |
| `tech_team_outputs.ph_task` — publish target | |
| `public."user"` — validator identity | |

🔴 **The decisive measurement — warehouse product titles are effectively absent for eBay:**

```
public.listing_data WHERE which_channel_name='ebay' AND is_ended=0
  ebay_rows   143,257
  with_title    1,447   →  1.0%
```

REQ-16 measured 8.3% on its scope; on this report's scope it is **1.0%**. `Best Seller` is
**unbuildable** from the warehouse. Conversely `order_transaction`, `traffic_data` and `ph_task` do
not exist in ledsone at all.

---

## 7. Evidence Map — post-audit grading

| # | Column | Source | Grade |
|---|---|---|---|
| 1 | Account | warehouse `order_transaction.ss_name` (+ `market_place`) | ✅ VERIFIED |
| 2 | Date | anchor = **R−1**, pinned explicitly (not `CURRENT_DATE`) | ✅ VERIFIED (decision B closed) |
| 3–4 | Today's / Yesterday Sales | `SUM(order_total)` at R−1 / R−2 | ⚠ **BLOCKED ON DECISION M** (status filter) |
| 5–6 | Sales Diff / Growth % | derived | ✅ VERIFIED |
| 7 | Same Day LY Sales | same query at the LY anchor | ⚠ decision C (calendar vs weekday) |
| 8–9 | Today's / Yesterday Orders | `COUNT(DISTINCT order_id)` | ⚠ **BLOCKED ON DECISION M** |
| 10 | Order Growth % | derived | ✅ VERIFIED |
| 11 | Same Day LY Orders | LY anchor | ⚠ decision C |
| 12 | Units Sold | `SUM(quantity)` | ⚠ decision H (period) + M |
| 13 | Avg Order Value | derived | ✅ VERIFIED |
| 14 | Best Seller | **ledsone** `ebay_listings.title` + order lines | ⚠ decision D (ranking basis) — **source confirmed** |
| 15 | Active Listing | warehouse `listing_data` **or** ledsone `ebay_listings` | 🔴 CONFLICT — decision K |
| 16–18 | AH Listing / Sales / Trend | **no source** | 🔴 UNAVAILABLE — decision A |
| 19–21 | PH Listing / Sales / Trend | **ledsone `staff.ph_categories` + `ph_category_products`** (28% coverage) · warehouse `order_transaction.user_name` for sales | ✅ **VERIFIED (partial coverage)** — was UNDEFINED |
| 22 | Account Sales Trend | threshold band on col 6 | ⚠ decision E (bands inferred) |

**Result: 6 VERIFIED · 3 VERIFIED-with-caveat · 8 blocked on a decision · 1 conflict · 3 UNAVAILABLE (AH).**

Net movement from the pre-audit grading: **PH moved from UNDEFINED to VERIFIED**, `Best Seller`'s
source is confirmed, the daily grain and timezone are cleared — and **a new blocker (M) appeared that
is more serious than any of the ones it replaced.**

---

## 8. 🔒 ADDENDUM — source lock and re-derivation on `ledsone` alone (owner instruction, 2026-07-23)

The owner instructed that only **two** MCPs be used, because they carry the live data:
`https://docs.ledsone.co.uk/mcp` (AIOS knowledge base) and `https://mcp.ledsone.co.uk/mcp` (raw
`ledsone` Postgres). **The warehouse `order_management_copy` is out of scope for this project.**
Sections 1–7 above were partly measured on the warehouse; this section re-derives the load-bearing
findings on `ledsone` alone.

### 8.1 The maturation finding HOLDS — re-measured on ledsone

`order_management.orders` joined to `sub_source (source_id = 2)`:

| Order day | `Completed` | Placed (≠Cancelled) | Matured | Sales `Completed` | Sales placed |
|---|---|---|---|---|---|
| 23 Jul (today) | 0 | 8 | 0.0% | — | £126.33 |
| **22 Jul (R−1)** | **36** | **142** | **25.4%** | **£928.58** | **£2,983.35** |
| 21 Jul (R−2) | 157 | 158 | 99.4% | £2,891.03 | £2,891.03 |
| 20 Jul | 147 | 149 | 98.7% | £2,847.04 | £3,321.84 |
| 19 Jul | 174 | 175 | 99.4% | £3,770.73 | £3,770.73 |
| 16 Jul | 143 | 143 | 100.0% | £2,697.93 | £2,697.93 |

**Decision M stands unchanged.** At R−1 only **25.4%** of orders have matured to `Completed`;
£928.58 against a true £2,983.35 — a **69% understatement** on ledsone's own numbers.

### 8.2 The warehouse is a mirror, and it differs

Same days, same filters, warehouse vs ledsone:

| Day | Warehouse `Completed` | ledsone `Completed` | Δ |
|---|---|---|---|
| 21 Jul | £2,884.11 / 152 | **£2,891.03 / 157** | −£6.92 / −5 orders |
| 20 Jul | £2,845.06 / 144 | **£2,847.04 / 147** | −£1.98 / −3 orders |
| 19 Jul | £3,783.17 / 174 | **£3,770.73 / 174** | +£12.44 / 0 |

Small (~0.2–0.4%) but real. **`ledsone` is the live source; the warehouse lags and diverges.** This
corroborates the owner's instruction.

### 8.3 Sales definition under the lock — and why it is an improvement

AIOS KB `database/postgresql/schemas/order_management/tables/orders.md` defines
`orders.total` as the **order grand total**, sourced from the same underlying `order_total` field the
warehouse mirrors. So the measure is unchanged in meaning — only the source moves.

✅ **It is also cleaner.** `orders.total` sits at **order grain** (one row per order). The warehouse
stores `order_total` at **line** level, which is precisely why REQ-13 needed `COUNT(DISTINCT
order_id)` to avoid double counting. That failure mode does not exist here.

⚠ **Consequence:** figures will not tie exactly to EBPD's published monthly numbers, which were built
from the mirror. Must be stated on the deliverable.

### 8.4 ✅ The publish target — resolved

`tech_team_outputs.ph_task` **does not exist in `ledsone`** (verified: zero matching tables). It lives
**only** in the warehouse, and it is how the `ebay_priors` audience receives every prior eBay report
(REQ-12, 13, 14, 16).

**Resolved the same day: the owner clarified the source lock governs DATA RETRIEVAL.** Every figure
in the report is retrieved through the two named MCPs; the output step is unaffected, so publishing
to `ph_task` remains the normal route. Decision **N** closed.

Publishing remains gated on the usual terms — explicit owner instruction, audience named and each
recipient verified beforehand (decision **J**) — and on the `ph_task` mechanics recorded in
`CLAUDE.md` §10 (no real `UNIQUE(task_id)`; `assigned_user_team` must be set; static-rendered HTML).

### 8.5 Corrections the AIOS knowledge base forced

The KB had **not** been consulted when sections 1–7 were written. Reading it corrected four things:

| # | Was | Actually |
|---|---|---|
| 1 | "PH = Product Holder" | **Portfolio Holder** — *"a sales team member accountable for a set of products across platforms"* |
| 2 | `Active Listing` = choose REQ-13's or REQ-16's definition (decision K) | **`all_list = 1`** — the KB states *"Do not use `is_child`/`is_parent` combinations."* **Decision K is settled by the KB**, and both prior definitions were wrong |
| 3 | eBay PH sales join on `item_id` | `order_item_info.item_id` **also stores Shopify product IDs** — the `sub_source.source_id = 2` filter is **essential** |
| 4 | `ref_id` treated as one thing | **Polymorphic** — eBay = item ID, Amazon = ASIN, B&Q = EAN |

Also: `order_item_info.item_price` / `item_quantity` are **VARCHAR** and must be CAST; staff names
resolve via `staff.users` **only**.

**A canonical eBay PH sales query already exists** at `business/queries/ph-sales-by-channel.md`. This
project was reconstructing from scratch what was already documented. **Read the KB first.**

### 8.6 AH — now searched in all three places, and absent from all

| Searched | Result |
|---|---|
| ledsone (all columns: `holder`/`assigned`/`owner`/`ph_`/`ah_`) | `staff.ph_categories.user_id` is the **only** user linkage in the database. `sub_source` has no assigned-user column. |
| AIOS knowledge base — `"account holder"` | **0 results** |
| AIOS knowledge base — `"portfolio holder"` | 9 files, all PH |

**AH has no definition and no source anywhere in the estate.** Decision A is purely a question for
Thinesh.

### 8.7 🟠 Duplicate risk — a Portfolio Holder dashboard already exists

AIOS KB `infrastructure/postgres-access.md`: the same Postgres instance hosts a third database,
**`ph_dashboard`** — a Django app, *the Portfolio Holder dashboard* — with tables
`analytics_phmonthchannel`, `analytics_phtotalids`, `analytics_metricpoint`, `accounts_user`.

`analytics_phmonthchannel` (PH × month × channel) is adjacent to this report's PH columns and must be
checked before REQ-17 builds its own.

⚠ **It is not readable with current credentials** — `dbhub_readonly` has **no grants** on
`ph_dashboard`; the `ph_pgsql` role (added 2026-07-17) would be needed. Recorded as decision **O**.

---

## 9. What still needs running

- ⬜ Confirm `order_transaction.user_name` is the PH holder.
- ⬜ How far back the LY comparator is populated, **per account** (accounts under a year old must
  render blank, never zero).
- ⬜ Which `Active Listing` definition to adopt, and the size of the gap today (decision K).
- ⬜ One account-day reconciled by hand to a figure Thinesh can verify in Seller Hub.
- ⬜ Restatement behaviour: if this is an accumulating track (decision I), a row written for R−1
  today will change as orders mature and refunds land. Freeze or restate?
