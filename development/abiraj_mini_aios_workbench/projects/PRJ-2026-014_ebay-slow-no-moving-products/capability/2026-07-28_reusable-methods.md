# eBay Slow / No-Moving Products (ESNM) — Reusable Methods (Capability Extract)

> Reusable, generalisable techniques extracted from this project's build. Methods worth reusing on
> other projects — not project-specific facts.
> **What this project does:** a per-listing eBay slow/no-moving report (20 source columns) plus a
> 12-rule ordered action-recommendation engine, across all LEDSone eBay accounts on UK + Germany.
> **Source:** `PROJECT_HOME.md`, `SYSTEM_REFERENCE.md`, `validation/REQ-16_.../`.

## 1. Ordered "first-match-wins" rule engine
Model an action-recommendation set as a **priority-banded gate list**: Critical → High → Medium →
Low, first match wins, and within a band the lower rule number wins. Evaluation order is explicit
(1→2→3→4→5→7→8→9→10→11→12) so precedence is deterministic and auditable. A **fallback bucket**
("Monitor — no rule matched") catches every unmatched row so nothing is silently dropped.
*Reusable for any triage/action-assignment problem.*

## 2. Thresholds as configuration, never code
Every rule threshold lives in editable yellow cells on a workbook **Rules** sheet; the action column
is a live formula referencing them, so changing one cell re-evaluates all rows. Keeps business logic
tunable by the owner without touching code.

## 3. Build the engine twice, independently, then diff
Implement the same logic two ways — live Excel formulas and Python — and diff row-by-row
(here: 11,156/11,156, zero mismatches, zero formula errors). Reconcile one sampled row field-by-field
against the live DB. Agreement between two independent implementations is the verification.

## 4. Two-database joins — know which domain lives where
This report needs **two** databases and neither can build it alone: listings/sales/PPC from
`ledsone`, but organic **traffic exists only in the warehouse** `order_management_copy.public.traffic_data`
(`which_channel = 2`). Confirm per-domain source before assuming one DB is enough.

## 5. Blank ≠ zero for missing data
Where a data source is absent (missing traffic rows, unavailable Watchers), the column ships
**blank, never `0`** — a zero would mislead a rule into firing. Rules 5 and 9 are evaluated only
where a traffic row exists; the missing-data column stays empty.

## 6. Deterministic output ordering for byte-identical rebuilds
When many rows tie on the sort keys, add a stable final tiebreaker (here `item_id`) to the SELECT's
ORDER BY. Without it an unordered SELECT emits identical data in a different order each run and the
payload hash drifts. Two consecutive runs should produce a byte-identical payload.

## 7. Anchor scheduled jobs on a complete period
"Today" is a partial day and inflates/deflates counts between rebuilds. Scheduled runs anchor on the
**last day of the previous calendar month**; ad-hoc runs use the last **complete** day.

## 8. Don't inherit a filter that doesn't apply to your path
The warehouse's standing "always filter `wrong_sku = 0`" rule exists for SKU→inventory bridging.
This report does not bridge to inventory, so filtering it would delete 51.7% of real, sellable
listings. Filters travel with the access path, not the table — apply deliberately.

## Gotchas / traps
- **Watchers has no source in either database.** Every column was scanned for
  `watch`/`favorite`/`wishlist`/`saved`; only unrelated `staging_ai.watched_status` hits. eBay
  exposes Watchers only via the Trading API, which is not ingested. **Rule 6 can never fire**;
  column 17 ships blank.
- **Structurally unreachable rules exist.** Rule 10 ("age >180d AND last sale >90d ago") is always
  claimed first by Rule 1, so it matched 0 rows — a property of the rule set, not a data fault.
- **eBay traffic ingestion lost 11 of 91 days** in the window (eBay-specific; Shopify unaffected).
  Views understated ~12% over 90 days, ~23% over 30 days — degrades Rules 5 and 9.
- **PPC coverage trade-off:** `ledsone.ebay_campaigns.performance_data` = 65 days but complete
  (incl. SMART); warehouse `ppc_performance` = 90 days but omits SMART at ad grain. Built on
  `ledsone`; Rule 8 runs on 30 days, fully covered.
- **Assumed thresholds must be flagged:** rule precedence and Rule 8's £5.00/30d floor are invented
  (source defines neither) — disclosed on the report, precedence drives the 72.3% Critical count.
- `ebay_listings.status` is ~99% NULL — derive Listing Status from `is_ended`/`end_date` instead.

## Key sources
- Listings — `ledsone` `listings.ebay_listings` (scope `is_ended=0 AND is_child=0`, `site IN ('UK','Germany')`)
- Accounts — `ledsone` `order_management.sub_source` (`source_id = 2`)
- Sales — `ledsone` `order_management.orders` + `order_item_info` (join `orders.id = order_item_info.order_id`, aggregate by `item_id`)
- eBay PPC — `ledsone` `ebay_campaigns.performance_data`
- Traffic — warehouse `order_management_copy` `public.traffic_data` (`which_channel = 2`)
- Units — `COALESCE(NULLIF(real_qty,'')::numeric, NULLIF(item_quantity,'')::numeric, 0)`; `Cancelled` excluded, `Refunded`/`Inprogress` included.

## Automation pattern
- **Pre-compute-then-serve:** D01 is three artefacts (HTML dashboard, xlsx workbook, governed JSON)
  over one dataset; both renderers import the same `fetch()`/`assemble()` so they cannot drift.
- **Cadence:** monthly, 2nd at 09:45 (Windows task `ESNM_Monthly_Slow_No_Moving`; 09:45 not 09:30
  to avoid EBPD colliding on the shared `temp_user` login).
- **Publish:** `automation/publish_esnm_ph_task.py` writes one `tech_team_outputs.ph_task` row per
  recipient for the `ebay_priors` audience (ph_task 411–414). Dry-run by default, artefact sanity
  guards, and **SELECT-then-UPDATE** because there is no unique constraint on `task_id` (a blind
  INSERT would duplicate). Set `assigned_user_team` explicitly — absent from the sample DDL but
  required or the row never reaches the audience.
