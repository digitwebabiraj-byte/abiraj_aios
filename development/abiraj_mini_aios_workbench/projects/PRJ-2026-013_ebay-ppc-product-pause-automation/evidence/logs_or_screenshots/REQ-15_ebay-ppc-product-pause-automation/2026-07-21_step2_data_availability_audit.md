# Step-2 Data Availability Audit — REQ-15 eBay PPC Product Pause Automation

**Executed:** 2026-07-21 · read-only · live warehouse (`order_management_copy`) via Postgres MCP
**Question asked by the owner:** *"is there needed all data in the live db?"*
**Scope confirmed by the owner:** stock data + eBay campaign performance data, **LEDSone account,
marketplace UK**.

## Verdict

**GREEN with four named gaps.** The rule engine in the mockup **can be driven from live warehouse
data at listing grain** — and with *better* inputs than the mockup had (real, separate 30D / 14D /
7D windows instead of one 7-day export reused three times). Four structural gaps mean the delivered
system will not be a 1:1 clone of the mockup; each is stated below with its consequence.

## Account identification

| Mockup label | Live value |
|---|---|
| Account "LEDSone" | `ss_name = 'led_sone'` (exact match — never `LIKE`) |
| Marketplace "UK" | `marketplace = 'UK'` |
| Channel eBay | `source = 2` |

Marketplaces US and DE also appear in the mockup's switcher; the owner scoped this build to **UK**.

## Check 1 — Does eBay PPC performance data exist? ✅ YES

`public.ppc_performance`, `source=2`, `ss_name='led_sone'`, `marketplace='UK'`, last 90 days:

| Grain | Rows | Entities | Distinct item_ids | Date range | Spend |
|---|---|---|---|---|---|
| `record_type='campaign'` | 10,084 | 119 campaigns | 0 (campaign grain has no ref_id) | 2026-04-22 → 2026-07-21 | £15,763.62 |
| `record_type='ad'` | 337,338 | 4,883 ads | **2,362** | 2026-04-22 → 2026-07-20 | £12,968.41 |

**Listing-grain data exists** (`ad` rows carry `ref_id` = eBay item_id). Daily date grain means the
30D, 14D and 7D windows every rule needs are all computable.

⚠ **History starts 2026-04-22 (~90 days).** Enough for 30D windows; a 12-month trend is not
available.

## Check 2 — Campaign metadata / state ✅ YES (`public.ppc`)

`record_main_type='campaign'`, led_sone UK:

| record_subtype | bidding_strategy | record_status | n |
|---|---|---|---|
| ON_SITE (Advanced/CPC) | MANUAL | running | 23 |
| ON_SITE | SMART | running | 8 |
| ON_SITE | MANUAL | paused | 4 |
| ON_SITE | SMART | paused | 1 |
| ON_SITE | MANUAL / SMART | ended | 9 |
| COST_PER_SALE (Standard/CPS) | — | running | 73 |
| COST_PER_SALE | — | deleted | 16 |
| OFF_SITE | — | ended / deleted | 3 |

This supplies the mockup's **Campaign ON/OFF** column (`record_status`) and its **Type
Manual/Smart** column (`bidding_strategy`) directly. `record_status` values are
`running / paused / ended / deleted / archived` — richer than the mockup's binary ON/OFF.

## Check 3 — Stock ✅ YES, with a grain problem (see Gap C)

Bridge (per the `ppc-stock-lookup` standard): `ppc_performance.ref_id` →
`listing_data` (`which_channel=2`, `market_place`, `sub_source`, `wrong_sku=0`) →
`COALESCE(NULLIF(mapped_sku,''), sku)` → `location_wise_inv_stock` (`location='UK'`).

Measured over the 30D advertised item_ids:

| Metric | Value |
|---|---|
| Distinct item_ids advertised in 30D | 2,117 |
| Bridged to at least one SKU | **1,952 (92.2%)** |
| Unbridged (no stock resolvable) | 165 (7.8%) |
| **Mapping to MORE THAN ONE SKU** | **1,696 (80.1%)** |
| Max SKUs on a single item_id | **245** |

## Check 4 — End-to-end engine dry run ✅ PASSES

The mockup's full ordered engine (Stock floor 5 → Rule 1 ACOS>=40 with 7D<20 rescue → Rule 2 14D
0 orders + >=20 clicks with <£2.50 rescue) executed live against **running ON_SITE campaigns**,
30D window anchored on the latest loaded date (2026-07-20):

| Decision | Listings | 30D spend at stake |
|---|---|---|
| Keep running | 678 | £1,658.64 |
| **PAUSE — Rule 2** (clicks, no sales) | **8** | £57.25 |
| **PAUSE — Rule 1** (high ACOS) | **3** | £48.49 |
| NO STOCK DATA (unbridged) | 33 | £30.82 |
| **PAUSE — Stock** (<5 units) | **10** | £11.38 |

**21 real pause candidates.** The engine is buildable. (Grain is item × campaign — 732 rows from
610 distinct item_ids, because one listing can run in several campaigns; see Gap D.)

Query preserved at `../../../sql/REQ-15_ebay-ppc-product-pause-automation/eppa_rule_engine_dryrun.sql`.

---

## The four gaps

### Gap A — SMART campaigns have NO listing-level data 🔴
8 **running** ON_SITE SMART campaigns spent **£755.36** in 30D and returned **0 item_ids** at `ad`
grain — they exist only at campaign grain. The mockup shows SMART listings as ordinary rows
(e.g. `JD | Target Mixed | New | ST | smart`); that is not reproducible.
**Consequence:** SMART campaigns can only be evaluated **whole-campaign**, or excluded. A pause
decision there pauses the entire campaign, not one listing. **Business decision required.**

### Gap B — ON_SITE vs COST_PER_SALE must never be combined 🔴
Standing warehouse rule: eBay Advanced (ON_SITE/CPC, charged per click) and Standard
(COST_PER_SALE/CPS, charged as a % of sale) use incompatible pricing models — their spend/sales/ACOS
are not comparable and must never be summed. **CPS ACOS is mechanically near-constant** because
spend is a fixed cut of sales, so an ACOS-ceiling rule is close to meaningless on it.
Live 30D at ad grain: ON_SITE running 610 item_ids / £1,873.46 · COST_PER_SALE running 1,840
item_ids / £1,286.52.
**Consequence:** the dry run above deliberately covers ON_SITE only. Whether Standard campaigns are
in scope — and under what rule, since Rule 1 does not transfer — is a **business decision**.

> Note for the knowledge base: the `ppc-stock-lookup` reference states *"eBay `record_type='ad'`
> exists only for COST_PER_SALE; ON_SITE is campaign-grain with no ref_id/SKU."* **That is not true
> for this account** — ON_SITE MANUAL campaigns carry 610 item-level ref_ids. It *is* true for
> ON_SITE **SMART**. The reference should be corrected to split by `bidding_strategy`.

### Gap C — "Units in stock" is not a single number for 80% of listings 🟠
An eBay listing is a multi-variant container: **1,696 of 2,117 (80.1%)** advertised item_ids map to
more than one SKU, one to **245**. The mockup assumes one integer per listing ("82 units"). The dry
run used `SUM(stock)` across variants, which is *an* assumption, not a confirmed rule — and it is
the permissive one (a listing whose top-selling variant is at zero still looks healthy).
Options: SUM across variants · MIN · "any variant out of stock" · restrict to the advertised
variant. **Business decision required** — this changes which listings get paused.
Also: 165 item_ids (7.8%) do not bridge at all → the report must show them as **NO STOCK DATA**,
never as zero (reporting "0" would auto-pause a listing that may be fully stocked).

### Gap D — Two mockup fields do not exist in the warehouse 🟠
- **Listing state (ON/OFF)** — `public.ppc` holds eBay `campaign` and `ad_group` rows only; there is
  no `ad`-grain status row for eBay. The mockup's separate "Listing ON / Listing OFF" line has no
  live source. Campaign state is available; listing state is not.
- **Listing price** — not present in the PPC tables (it is `0` in the mockup too). It is reachable
  from the `ledsone` DB `listings.ebay_listings` if a rule ever needs it; no current rule does, so
  it is out of scope unless a Custom Rule uses the `price` metric the mockup offers.

Also carried over: `location_wise_inv_stock` holds **live stock only, no history** — a windowed
spend figure is always paired with *today's* stock. This must be stated on the report.

---

## What is NOT blocked

All five thresholds are editable inputs (stock floor 5 · ACOS ceiling 40% · ACOS rescue 20% ·
clicks min 20 · spend floor £2.50), sourced from the `Pause Rules` sheet, and must stay
configuration — never hardcoded, per the FRRC precedent.

## Standing constraint (unchanged by this audit)

Actually **pausing** an eBay campaign is a write to live PPC. That falls under the workbench's
*Never Touch Without Written Approval* list on two counts ("live automation" and "financial or PPC
business logic"). No such approval exists. The delivered system is therefore a **read-only
recommendation report** with the staff Approve/Reject column the mockup already provides; a human
executes the pause in Seller Hub.

## Evidence integrity

All figures above were produced by executed read-only queries against the live warehouse on
2026-07-21. No writes, no DDL, no publish. Sources imported COPY-only, SHA-256 recorded in
`../../source_documents/REQ-15_.../SOURCE_MANIFEST.md`.
