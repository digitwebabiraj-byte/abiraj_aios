# CLAUDE.md — PRJ-2026-015 Daily Sales Track

Project execution rules. Inherits the workbench `CLAUDE.md`; the rules below are additional and
specific to this project.

## Identity

- Project `PRJ-2026-015_daily-sales-track` · code `dst` · Task `REQ-17_daily-sales-track`.
  Owner/dev Abiraj; Business Validator Thinesh.
- ⚠ **The IDs and the project name are pending owner confirmation** (decision L). The name is
  deliberately **channel-neutral** — the source never names a channel, and a project ID must not be
  renamed later.
- A new day or session does **not** mint a new Task ID. Keep `REQ-17` until a genuinely new
  requirement earns one.

## 1. Do not invent the missing logic — this source has none

The single most important fact about this project.

`Thinesh task (4).xlsx` contains **no business logic whatsoever**. Every cell that looks like a
formula is a **constant typed with a leading `=+`** — cell `E2` holds the literal string `=+435.3`,
not `=C2-D2`. There is no rule table; the equivalent of REQ-16's canonical rows 20–32 **does not
exist in this file**.

Therefore **every definition must be either inherited from a governed project or raised as a
decision.** Do not infer business rules from the six sample rows. Inferring would produce a
plausible, fully-populated, silently-wrong daily report — and a second sales number that disagrees
with the published monthly one.

The one exception, and it is narrow: **the sample's arithmetic relationships are verified and may be
used** (32 of 32 re-derived exactly — see the SOURCE_MANIFEST). Those fix *how the columns relate*,
not *what feeds them*.

## 0. 🔒 SOURCE LOCK — owner instruction 2026-07-23

**Scope of this rule: DATA RETRIEVAL.** Every figure in this report is retrieved through these two
MCPs and no others. It does **not** govern the output step — publishing the finished report to
`tech_team_outputs.ph_task` (warehouse) remains the normal route, on the usual terms: explicit owner
instruction, audience named and each recipient verified first (decision **J**).

**For retrieving data, use ONLY these two MCPs. They carry the live data.**

| MCP | URL | Role |
|---|---|---|
| `Ledsone-aios-mcp` | `https://docs.ledsone.co.uk/mcp` | **AIOS knowledge base** — read it BEFORE writing SQL |
| `Ledsone-db-mcp` | `https://mcp.ledsone.co.uk/mcp` | **Raw `ledsone` Postgres** — the only data source |

🔴 **Do NOT use the warehouse MCP** (`39dbecb8-…` → `order_management_copy`, :5435). It is a
**mirror**, it is not authoritative, and it is out of scope for this project. Measured divergence on
identical days: 21 Jul £2,884.11/152 orders (warehouse) vs **£2,891.03/157** (ledsone); 19 Jul
£3,783.17 vs **£3,770.73**. The warehouse also connects as **`postgres`** (full write) rather than a
read-only role — a second reason to stay off it.

**Read the AIOS knowledge base first.** It is not optional background: it already contains the
canonical query for this report's hardest columns (`business/queries/ph-sales-by-channel.md`) and it
corrected four things this project had wrong. Skipping it is the documented cause of EPC's first
wrong build.

## 2. Measurement definitions — ledsone-native

REQ-13's definitions came from the **warehouse**, which is now out of scope. The ledsone equivalents,
confirmed against the AIOS KB (`database/postgresql/schemas/order_management/tables/orders.md`):

| Measure | Definition (ledsone) |
|---|---|
| Sales | `SUM(order_management.orders.total)` — the KB defines `total` as the **order grand total**, sourced from the same underlying `order_total` field the warehouse mirrors |
| Orders | `COUNT(DISTINCT orders.id)` |
| Units | `SUM(CAST(order_item_info.item_quantity AS INT))` |
| AOV | Sales ÷ Orders |
| Channel | join `order_management.sub_source ss ON ss.id = o.sub_source_id AND ss.source_id = 2` |

✅ **This is cleaner than the warehouse, not a compromise.** `orders.total` is at **order grain** —
one row per order. The warehouse stores `order_total` at **line** level, which is why REQ-13 needed
`COUNT(DISTINCT order_id)` to avoid double-counting. That whole class of error disappears here.

⚠ **`order_item_info.item_price` and `item_quantity` are VARCHAR** — always `CAST` before arithmetic.
(AIOS KB, `business/queries/ph-sales-by-channel.md`.)

⚠ **Consequence to disclose:** figures will **not tie exactly to EBPD's published monthly numbers**,
which were built from the warehouse mirror. The differences are small (~0.2–0.4%) but real, and
ledsone is the live source. State this on the deliverable.

## 3. The anchor — CLOSED, and it is not what the headers say

✅ **Confirmed by the owner 2026-07-23.** This is a **daily automated** report. For a run on date **R**:

| Column | Actually means |
|---|---|
| `Date` | **R − 1** |
| `Today's Sales` · `Today's Orders` | **R − 1** — yesterday |
| `Yesterday Sales` · `Yesterday Orders` | **R − 2** — day before yesterday |
| `Same Day LY …` | the matching day one year before **R − 1** |

A report generated in the morning cannot show that morning's own trading.

⚠ **Pin the anchor explicitly — do NOT use `CURRENT_DATE`.** The warehouse runs on
**`Asia/Colombo (+05:30)`** while ledsone runs on **`Europe/London`**, so the warehouse's
`CURRENT_DATE` rolls over 4.5 hours before London's. (The stored `order_date` values are UK time in
*both* databases — verified by hour-of-day distribution — so `::date` bucketing itself is safe. It is
only `CURRENT_DATE`/`NOW()` that differ.)

⚠ **Show the reported date on the face of the report.** The headers still read "Today's" and
"Yesterday" but mean R−1 and R−2. Without the date visible, every reader will misread them.

## 3b. 🔴 The status filter — orders are not `Completed` on the day they are placed

**The single most important measurement in this project.** Orders enter as `New` (warehouse) /
`Inprogress` (ledsone) and reach `Completed` about **two days** later:

| Order day | `Completed` | Non-cancelled | % matured |
|---|---|---|---|
| **R−1** (22 Jul) | **37** · £1,102.43 | **141** · £3,010.04 | **26.2%** |
| R−2 (21 Jul) | 152 · £2,884.11 | 153 · £2,884.11 | 99.3% |
| R−4 (19 Jul) | 174 | 174 | 100.0% |

**REQ-13's inherited `order_status='Completed'` filter is therefore incompatible with the R−1
anchor** — it would report yesterday as £1,102.43 instead of £3,010.04, a **63% understatement**,
beside a fully-matured R−2 column. Every daily report would show a collapse that did not happen.

**Do not resolve this by writing code.** It is decision **M**, owned by Thinesh and Sajeesan. Until
it closes, do not ship a sales figure. If option (a) is chosen (count orders *placed*, excluding
`Cancelled` only), the divergence from REQ-13 **must be stated on the deliverable** — the daily
report will not tie to EBPD's monthly figure on the most recent ~2 days.

⚠ Status enums differ between the databases — warehouse `New` vs ledsone `Inprogress`. Do not assume
they are identical.

## 3c. AH / PH — zero vs blank (owner instruction 2026-07-23)

**AH = the PH remainder.** A live listing with **no** PH category assignment belongs to the account's
AH, so per account `AH Listing + PH Listing = total live listings`. Measured 2026-07-23 (`all_list=1`,
`is_ended=0`): **14,607 = 2,750 PH + 11,857 AH** across 13 accounts.

**Where an account has no PH-assigned listings, write `0` — not blank.** Owner instruction, and it is
correct: seven accounts (`coventrylights`, `vintageinterior`, `dctransformer`, `re6865`,
`lighting_sone`, `homin_gmbh`, `bestbringer`) genuinely have **zero** PH assignments. That is a real
measurement, not missing data.

⚠ **This does not weaken §4.** `0` is right where the true count is zero. **Blank** remains right
where the figure is *unknown or not applicable* — above all `Same Day LY` for an account that did not
exist a year ago. Never collapse "didn't trade" into "traded £0".

## 4. Missing data renders blank, never zero

A `0` in a sales, orders or growth column is **indistinguishable from a real trading collapse** — and
detecting collapses is this report's entire purpose. This matters more here than in any prior
project in this workbench.

Applies to: an account with no orders that day (is it closed, or is the feed late?), an account
younger than a year (no LY comparator), and any day missing from the series. Each must be visibly
blank with a stated reason, never a zero.

## 5. Three columns are undefined — do not quietly drop or guess them

**Updated 2026-07-23 after the data audit — this was six, it is now three.**

✅ **PH = Product Holder is SOURCED.** The live assignment is ledsone `staff.ph_categories`
(category → `user_id`) + `staff.ph_category_products` (`ref_id` → category, `source_id = 2` for
eBay): **3,098 distinct eBay listings across 50 categories**. Warehouse
`public.order_transaction.user_name` carries the PH on the sales line directly, so PH *sales* need no
join. ⚠ Coverage is **28%** of the eBay portfolio — `PH Listing` must render **blank** for the other
72%, never `0`. ⚠ Prefer ledsone's `staff.*` tables over warehouse `analytics.ph_segment`, which is a
derived period report and was **9 days stale** when measured.

🔴 **AH = Account Holder is still UNSOURCED** (columns 16–18). ledsone has no account→user link at
all — `staff.ph_categories.user_id` is the only user linkage in the entire database, and
`order_management.sub_source` has no assigned-user column. The warehouse offers only
`staging_ai.cppc_platform_staff_ownership_v1` / `cppc_campaign_responsibility_registry_v1`, which sit
in the schema REQ-11 established as never promoted, and are advertising-scoped.

If a build is requested before decision A is closed, the columns must be **present and visibly
blank**, with the gap stated **inside** the deliverable — not silently omitted, and never populated
with a guess. Dropping them without saying so would let a reader believe the report is complete.

## 6. Read-only discipline

- **READ-ONLY on all source data** — warehouse `order_management_copy` and the `ledsone` DB. No
  INSERT/UPDATE/DELETE, no DDL, no schema change, no automation on any source table.
- The **only** approved write would be a guarded publish of the finished report to
  `tech_team_outputs.ph_task`, on explicit owner instruction, **after the audience is named and each
  recipient verified** (decision J). No audience is decided; **no publish may occur.**
- This project **recommends nothing and changes nothing** on any marketplace. There is no action
  column. Any request to add one is a new requirement.

## 7. Canonical patterns from the AIOS knowledge base — do not reinvent these

`business/queries/ph-sales-by-channel.md` is the authority for the PH columns. Four rules from it
that this project had **wrong** before reading it:

1. **PH = Portfolio Holder** — *"a sales team member accountable for a set of products across
   platforms"*. Not "Product Holder".
2. **The eBay listing filter is `all_list = 1`.** The KB says explicitly: *"Do not use
   `is_child`/`is_parent` combinations."* This overrides **both** REQ-13's and REQ-16's
   `Active Listing` definitions — decision **K** is settled by the KB, not by choosing between them.
3. **`order_item_info.item_id` also stores Shopify product IDs.** The
   `sub_source.source_id = 2` filter is **essential**, not cosmetic — without it, Shopify rows leak
   into eBay figures.
4. **`ref_id` in `staff.ph_category_products` is polymorphic** — eBay = item ID, Amazon = ASIN,
   B&Q = EAN barcode. Always filter `source_id = 2`.

The PH assignment chain:

```
staff.users → staff.ph_categories (user_id) → staff.ph_category_products (ph_category_id, ref_id, source_id=2)
            → listings.ebay_listings (item_id = ref_id, all_list = 1)
```

**Resolve staff names via `staff.users` only** — never search sub_source, brands or warehouses for a
person's name (KB, Step 1).

⚠ **A negative sweep is only valid for the source you name.** REQ-11 concluded "no eBay feedback data
exists anywhere" after sweeping one of two databases; it was live in the other. Under the source lock
that risk shifts: **search the AIOS KB before concluding anything is missing from `ledsone`.**

## 8. The daily grain is untested — establish it before publishing any figure

Every existing project in this workbench uses a monthly window or a rolling multi-day window.
Whether `order_transaction.order_date` is a date or a timestamp, and **what timezone its day boundary
falls on**, has never needed establishing. It does now, and getting it wrong shifts every figure in
the report by a partial day.

## 9. One generator module

The report and any future scheduled run must come from a **single** module. REQ-16 shipped a defect
where the workbook and the dashboard were built from separate fetches and drifted apart. One module
makes that impossible.

## 10. Publish gotchas (ph_task) — if and when decision J closes

- **No real `UNIQUE(task_id)`** in live, despite the sample DDL claiming one → `ON CONFLICT` fails
  and a blind INSERT silently duplicates the report. Use SELECT-then-UPDATE, or pre-DELETE + INSERT.
- **`assigned_user_team` is absent from the sample DDL but MUST be set**, or the row never reaches
  the audience.
- The viewer runs **no JavaScript** — HTML must be **pre-rendered static**.

## 11. Stop conditions (in addition to the workbench's)

- A build is requested that would **guess** at AH/PH rather than leave those columns blank.
- Any proposal to change REQ-13's inherited sales definitions inside this project.
- The daily series turns out to have gaps and a publish is requested anyway without disclosing them.
- Any request to add an action, recommendation or write-back to a marketplace.

## Vocabulary

`order_total` = settled paid revenue · anchor = the last **complete** trading day · D−1 = the day
before the anchor · LY = the same day one year earlier (calendar or weekday — decision C) ·
AH = Account Holder *(unconfirmed)* · PH = Product Holder *(unconfirmed)* · `ebay_priors` = the
candidate `ph_task` audience group · inherited = a definition taken verbatim from REQ-13.
