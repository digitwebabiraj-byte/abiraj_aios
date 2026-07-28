# Daily Sales Track (DST) — Reusable Methods (Capability Extract)

> Reusable, generalisable techniques extracted from this project's own files. These are
> methods worth reusing on other projects — not project-specific facts.
> **What this project does:** a daily eBay sales report, one row per **account × marketplace**
> (30 rows, 24 columns), comparing each day's sales/orders/units against the previous day and the
> same date one year earlier, refreshed in place every morning.
> **Source:** `PROJECT_HOME.md`, `SYSTEM_REFERENCE.md`, `automation/AUTOMATION_README.md`.

## Reusable rules / methods

### 1. Pick the grain that ties to the operator's own screen
DST is one row per **account × marketplace** (30 rows), not per account. The correction came from a
Seller Hub check: LEDSone UK read £837.93 for one marketplace while the combined account row read
£1,144.51 (UK + Germany blended). The rule: choose the grain where **every row ties to exactly one
screen the business already trusts**, and make that tie a permanent verification check.

### 2. Inherit measurement definitions verbatim — never re-derive
Sales / Orders / Units / AOV are inherited **verbatim from REQ-13 (EBPD)**, not re-derived. Deriving
sales a second way gives the business a daily number and a monthly number that do not reconcile —
the duplicate-truth condition the workbench exists to prevent. If a report is the daily/periodic
sibling of an existing one, treat definitions as EXTEND, not CREATE.
*Reusable across every account-performance report.*

### 3. State any deliberate divergence from the inherited definition on the deliverable
DST deliberately diverges from REQ-13 on one point only: it counts orders **placed** (excluding
`Cancelled`), not `Completed`, because `Completed` matures ~2 days late and would show a ~63%
one-day collapse that did not happen. Where you diverge from an inherited definition, keep the
divergence to the minimum, justify it, and **disclose it on the report** so a reader comparing the
two does not assume one is broken.

### 4. Date-free `task_id` for an in-place daily update
The output is a **snapshot that replaces**, not an accumulating history. The `task_id` deliberately
carries **no date**, so each morning's run updates the same four `ph_task` rows rather than
appending one set per day. Side benefit: with no stored history, a later refund cannot leave a stale
published figure behind.
*Reusable for any "refresh in place" scheduled report.*

### 5. Anchor on the last complete day, pinned as a literal
A morning run that anchors on `MAX(date)`/`CURRENT_DATE` measures a **partial day** and reports a
collapse every day (hit twice before — REQ-15 read 8 clicks/£1.39 vs a normal ~540-click day). DST
reports **R−1** and pins the anchor as a literal because the two servers' `CURRENT_DATE` differ by
4.5 hours (warehouse `Asia/Colombo`, ledsone `Europe/London`). Show the reported date on the face of
the report since the headers still read "Today's".

### 6. Missing data renders blank, never zero
A `0` in a sales or growth column is indistinguishable from a real trading collapse — and detecting
collapses is the report's entire purpose. Accounts younger than a year have no last-year figure and
render **blank**. Absent days must be hunted for explicitly (a daily series is far more sensitive
than a rolling 90-day one — one lost day reads as a total halt).

### 7. Expose inferred thresholds as editable config, never inline them
The Up/Stable/Down trend bands (±5%) were **inferred from six sample rows**, not stated in the
source. They ship as editable configuration echoed on the deliverable, never hard-coded into the
query.

## Gotchas / traps

### 🔴 The currency trap — never blend
`order_management.orders.total` is stored in the **marketplace's own currency, not GBP** (confirmed
by joining `order_management.order_info.currency`, which matches `amount_paid` exactly). **There is
no exchange-rate table anywhere in `ledsone`**, so nothing is converted. Every row shows its own
symbol and totals are reported **one row per currency**. The first build rendered every figure with
a pound sign and summed them: 20 of 30 rows were mislabelled and the headline read "+3.19% up" when
GBP had actually fallen 5.16% and EUR risen 26.23% — the blend hid a decline in the biggest market.
Three verification gates (row currency, own symbol, no blended total) now exist to stop that
returning.

### Seller Hub anchor = £837.93
LEDSone UK for 22 Jul reads **£837.93** on the per-marketplace Seller Hub screen. That figure is a
permanent reconciliation anchor for the account × marketplace grain.

### Active Listing is understated ~5–6%
`Active Listing` uses the KB-canonical eBay filter `all_list = 1` (not `is_child`/`is_parent`
combinations, which both prior definitions got wrong). It is understated by roughly 5–6% from stale
`is_ended` flags on listings that have actually ended.

### Other recorded traps
- **`order_total` ≠ `item_price × quantity`**; `shipping_template_price` over-states postage.
- **`COUNT(*)` counts order lines, not orders** — ~7% high; use `COUNT(DISTINCT order_id)`.
- **Product titles are only 8.3% populated in the warehouse** — take titles from `ledsone`.
- The **warehouse `order_management_copy` mirror diverges** from live `ledsone` (e.g. 21 Jul
  £2,884.11/152 vs £2,891.03/157) and is out of scope for data retrieval.

## Key sources

| Need | Path |
|---|---|
| Sales / orders / units | `order_transaction.order_total`, `COUNT(DISTINCT order_id)`, `SUM(quantity)` |
| Money value + currency | `order_management.orders.total` + `order_management.order_info.currency` |
| Site → currency map | `listings.market_place_id_mapping` (UK=GBP; DE/FR/IE/AT/IT/ES/NL=EUR; US=USD; CA=CAD) |
| Active listings | `listings.ebay_listings` filtered `all_list = 1` |
| Product titles | `listings.ebay_listings.title` |
| Seller-account resolution | `order_management.sub_source` (`source_id = 2` = eBay) |
| Data source lock | `Ledsone-db-mcp` (raw `ledsone` Postgres) + `Ledsone-aios-mcp` (KB, read before SQL) |

## Automation pattern

- **Cadence:** daily at **09:05** (not 09:00 — five minutes clear of FRRC's day-8 09:00 job on the
  shared `temp_user` login). The run itself takes ~10 seconds; timing is about fleet contention, not
  data readiness. This is the fleet's **first daily** job.
- **In-place publish:** refreshes `tech_team_outputs.ph_task` **ids 422–425**, audience
  `ebay_priors`, via direct `psycopg2` (no MCP). Write is SELECT-then-UPDATE because **there is no
  UNIQUE constraint on `task_id`** despite the sample DDL claiming one, and `assigned_user_team`
  **must be set** (absent from the sample DDL; without it the row never reaches the audience).
- **Fail closed:** eleven gates (≥20 rows, ≥20 orders, money non-zero, every row has a currency,
  AH+PH=Active, reported day is in the past, collapse guards on rows/orders, dashboard ≥20 KB). A bad
  pull publishes nothing and the previous day's report stays live and untouched.
- **Collapse guard baseline** lives in `dst_last_good.json`, written only after a successful publish;
  on a fresh machine it has no baseline and skips itself by design.
- **Shared credential store:** two passwords in git-ignored `dst_secrets.bat` (copied from
  `dst_secrets.template.bat`); the whole fleet publishes through the same restricted `temp_user`
  login — which is periodically **locked out** when a `postgres` app leaks idle connections past the
  100-connection cap.
- **🔴 OneDrive no-run risk:** `0xC000013A` (`3221225786`) with an empty log means the job **never
  started** — the OneDrive hydration trap, not a code failure (it silently killed the `UDESC` job on
  2026-07-22). It presents as a silent no-run; watch `check_status.bat` the first few mornings. The
  durable fix is moving the repo off OneDrive to `C:\dev\`.
