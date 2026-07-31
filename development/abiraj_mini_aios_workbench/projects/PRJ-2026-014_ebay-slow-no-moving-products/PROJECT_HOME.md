# PROJECT_HOME — eBay Slow Moving & No Moving Products (ESNM)

| Field | Value |
|---|---|
| **Project ID** | `PRJ-2026-014_ebay-slow-no-moving-products` |
| **Project code** | `esnm` |
| **Task ID** | `REQ-16_ebay-slow-no-moving-products` |
| **Status** | **REQ-16-D01 DELIVERED · VERIFIED · PUBLISHED · AUTOMATED · BUSINESS-VERIFIED** (ph_task 411-414, `ebay_priors`, v7 · monthly job next run 2026-08-02) — **dashboard verified by Thinesh 2026-07-23**; technical/queryability/coordination sign-off still open |
| **Opened** | 2026-07-22 |
| **Owner** | Abiraj |
| **Coordinator** | Varmen |
| **Technical Reviewer** | Sajeesan |
| **Queryability Reviewer** | Tamil Selvan |
| **Business Validator** | **Thinesh** (requester) — verified live in `public."user"` (id **63**, `user_name` `Thinesh`, status **Active**; single exact match). Publish audience **`ebay_priors`** — closed 2026-07-22, see decision ~~E~~. |

> ⚠ **ID approval pending.** The source file carries **no requirement number**. `REQ-16` continues
> the eBay sequence — REQ-12 (`epc`), REQ-13 (`ebpd`), REQ-14 (`ERA`), REQ-15 (`eppa`) — and
> `PRJ-2026-014` follows `PRJ-2026-013`. Both still need owner confirmation.

## Business question

> Across the LEDSone group's eBay accounts on the **UK and Germany** marketplaces, which listings are
> **slow moving or not moving at all**, and **what specific action** should be taken on each one —
> end it, discount it, bundle it, re-price it, fix its listing quality, or leave it alone?

## Scope

**In scope (confirmed by the owner, 2026-07-22):**
- Channel **eBay** only.
- **All active eBay seller accounts** — explicitly *not* only the three named in the source sample.
- Marketplaces **UK and Germany** only.
- **Sellable listing rows only**: `is_ended = 0 AND is_child = 0`.
- Row key **account × marketplace × listing**.
- History **last 90 days**, plus the same 90-day window one year earlier for the year-on-year test.

Resulting universe — **12 accounts · 16 account × marketplace combinations · 11,156 listings**
(UK 7,685 · Germany 3,471), measured live 2026-07-22.

**Out of scope / blocked:**
- **Marketplaces other than UK and Germany.** France, US, Ireland, Italy, Spain, Netherlands,
  Austria and Canada listings exist (LEDSone alone sells on 10 sites) but are excluded by the
  owner's scope decision.
- **`neighbourmarket`** — a live eBay account with 345 active listings, but **US-only**, so it has
  no UK/DE rows and does not appear.
- **Any write to eBay.** The report **recommends**; ending, discounting, bundling or re-pricing a
  listing stays a human action in Seller Hub. Executing any of them is covered by *Never Touch
  Without Written Approval* ("live automation").
- Amazon and Shopify — same business question, separate requirement.

## Sources

Single source, imported COPY-only with SHA-256 recorded —
`evidence/source_documents/REQ-16_ebay-slow-no-moving-products/SOURCE_MANIFEST.md`.

**Rows 20–32 (the rule table) are canonical** for business logic. **Rows 1–11 are a fabricated
sample** that fixes the column order and nothing else — see the four provenance warnings in the
manifest, in particular that the sample's own `Action Required` values contradict the rule table
and therefore cannot be used to infer precedence.

## Current position

**REQ-16-D01 built, independently verified and published.** Anchor **2026-07-22**,
**11,156 listings** at the moment of verification.

⚠ **These counts drift between rebuilds** because the anchor is today and today is still
accumulating orders — a later rebuild produced 11,176 listings / 8,066 Critical. The figures
below are the **verified baseline**, not a fixed truth. See decision **H**.

| Priority | Rule | Action | Listings |
|---|---|---|---|
| 🔴 Critical | 1 | End Listing / Clear Stock | **8,067** (72.3%) |
| 🟠 High | 2 | Run Clearance Promotion | 1,210 |
| 🟠 High | 3 | Reduce Price by 5–10% | 851 |
| 🟠 High | 7 | Bundle with Best Seller | 149 |
| 🟠 High | 4 | Review Competitor Pricing | 42 |
| 🟠 High | 5 | Improve Images & SEO Title | 26 |
| 🟠 High | 8 | Pause PPC Campaign | 2 |
| 🟡 Medium | 9 | Improve SEO & Increase Promotion | 476 |
| 🟡 Medium | 10 | Refresh or Relist Listing | **0** — structurally unreachable |
| 🟡 Medium | 6 | Send Offer / Discount | **0** — no data exists |
| 🟢 Low | 11 | Maintain Current Strategy | 109 |
| 🟢 Low | 12 | Increase Stock & PPC Budget | 53 |
| — | — | Monitor — no rule matched | 171 |

The rule engine was implemented **twice, independently** — once as live Excel formulas driven by an
editable threshold sheet, once in Python — and the two agree on **11,156 of 11,156 rows, zero
mismatches**, with **zero formula errors** anywhere in the workbook. A sampled row was reconciled
field-by-field to the live database. All ten PASS/FAIL rules in `TASK_REGISTER.md` are green.

**This project needs two databases.** Listings, sales and PPC come from `ledsone`; organic traffic
(Views, Conversion Rate) exists **only** in the warehouse `order_management_copy` —
`public.traffic_data WHERE which_channel = 2`. See `CLAUDE.md` §2.

## Published — REQ-16-D01 is LIVE

**Published to `tech_team_outputs.ph_task` for the `ebay_priors` audience** — one row per recipient.
First published 2026-07-22 to the four then in scope; **Sharmilan and Sivajitha added 2026-07-31**
on owner instruction (both already `ebay_priors` members receiving the other eBay reports, both
verified live in `public."user"` before writing), bringing it to **all six**:

| ph_task id | assigned_user | task_id | version |
|---|---|---|---|
| **411** | Thinesh | `esnm_Thinesh_…` | v8 |
| **412** | Jarsini | `esnm_Jarsini_…` | v8 |
| **413** | kobiga | `esnm_kobiga_…` | v8 |
| **414** | powsteena | `esnm_powsteena_…` | v8 |
| **516** | Sharmilan | `esnm_Sharmilan_…` | v1 |
| **517** | Sivajitha | `esnm_Sivajitha_…` | v1 |

Publisher: `automation/publish_esnm_ph_task.py` — dry-run by default, artefact sanity guards, and
SELECT-then-UPDATE because **there is no unique constraint on `task_id`** despite the sample DDL
claiming one (a blind INSERT would silently duplicate the report). `assigned_user_team` is set
explicitly; it is absent from the sample DDL but without it the row never reaches the audience.

⚠ `description` is deliberately **NULL** — the portal renders it as a panel above the report and it
was consuming ~90px of an already short embed. Every caveat it carried is stated on the report.

✅ **Decision E (publish audience) is CLOSED** — `ebay_priors`, on the owner's instruction
2026-07-22.

## Known gaps — measured, not assumed

| # | Gap | Effect |
|---|---|---|
| 🔴 1 | **Watchers has no source in either database.** Every column in both was scanned for `watch`/`favorite`/`wishlist`/`saved`; the only hits are unrelated `watched_status` fields in `staging_ai`. eBay exposes Watchers only via its Trading API, which is not ingested. | Column 17 is delivered **blank**. **Rule 6 can never fire.** |
| 🔴 2 | **eBay traffic ingestion lost 11 days** inside the 90-day window — 7–11 May (5 days), 26 Jun + 29 Jun–1 Jul (4 days), 26 Apr, 18 Jul. Only **78 of 91 days** present. It is **eBay-specific, not a pipeline outage**: Shopify loaded normally on every one of those dates. **Root cause is not recorded in either database** — no log table covers the job that writes `traffic_data`. | Views understated ~12% over 90 days, **~23% over the 30-day window**. Degrades Rules 5 and 9. Mitigated by evaluating those rules **only** where traffic rows exist; absent traffic renders **blank, never zero**. Likely recoverable by re-running the eBay Analytics pull. |
| 🟠 3 | **eBay PPC — a trade-off, not a limit.** 📌 *Corrected 2026-07-22:* a 90-day figure **does** exist. `ledsone` `ebay_campaigns.performance_data` = **65 days but complete, incl. SMART**; warehouse `ppc_performance` = **90 days but omits SMART at ad grain** (£31,481.20 ad vs £39,454.11 campaign — a £7,973 gap, matching the EPPA finding). | Built on **`ledsone`** (complete but shorter). Rule 8 runs on a **30-day** window, fully covered by both. |
| 🟠 4 | **Rule 10 is structurally unreachable.** Any listing meeting "age >180d AND last sale >90d ago" necessarily has zero 90-day sales, so Rule 1 (Critical) always claims it first. | Rule 10 matched **0 of 11,156**. Not a data fault — a property of the rule set. See decision **C**. |
| 🔴 5 | **51.7% of in-scope listings carry `wrong_sku = 1`** (5,767 of 11,156) — but they are **real, live, sellable listings** with proper titles, stock and prices (e.g. `265660320119`, 248 units, £18.59). The flag only means the SKU string is not a clean inventory code. | **`wrong_sku` is deliberately NOT filtered** — excluding it would delete half the portfolio from a dead-stock report. The warehouse's standing "always filter `wrong_sku = 0`" rule applies to SKU→inventory bridging, a path this report does not use. **Disclosed:** column 4 (SKU) is unreliable for those rows and none of them bridge to inventory. |
| ✅ 6 | **Scope discrepancy RESOLVED — not stale data.** `ledsone` returns 11,156 (`is_ended=0 AND is_child=0`); the warehouse returns 10,739 distinct `ref_id`. The two encode parent/child differently: in warehouse `listing_data`, `is_child = 0` yields only **890** rows, exactly equal to `is_parent = 1`, so its sellable grain is `is_child = 1`. The warehouse also applies `wrong_sku = 0`. | The counts are **not comparable and neither is wrong**. `ledsone`'s **11,156** is the correct universe for this report. |

## Open decisions — required before D02 / D03

| # | Decision | Who | Why it matters |
|---|---|---|---|
| **A** | **Watchers** — drop Rule 6 permanently, or keep column 17 blank pending a new Trading-API ingestion? | Thinesh | Decides whether the deliverable is "20 columns, one permanently blank" or "19 columns". |
| **B** | **Traffic backfill** — re-run the eBay Analytics pull for the 11 lost days before sign-off, or accept understated Views? | Coordinator + the pipeline owner | Rules 5 and 9 stay measurably degraded until closed. The root cause is outside both databases. |
| ~~C~~ | ~~Rule precedence and the fate of the unreachable Rule 10~~ | — | **CLOSED 2026-07-23 — CONFIRMED BY THINESH.** Precedence stands as built: Critical → High → Medium → Low, first match wins, lower rule number wins within a band. **Rule 10 stays shadowed and is accepted as dead.** |
| ~~D~~ | ~~Run cadence and whether this becomes a scheduled job~~ | — | **CLOSED 2026-07-22 — monthly, 2nd at 09:45.** Registered as `ESNM_Monthly_Slow_No_Moving` against the main tree; next run 2026-08-02. 09:45 not 09:30 because EBPD holds Mon 09:30 on the same shared `temp_user` login and the 2nd lands on a Monday often enough to collide. |
| ~~E~~ | ~~Publish audience~~ | — | **CLOSED 2026-07-22 — `ebay_priors`** (Thinesh · Jarsini · kobiga · powsteena), all four verified present in the audience before writing. Published as ph_task 411-414. |
| ~~F~~ | ~~Actionability — 72.2% of rows carry one Critical action~~ | — | **CLOSED 2026-07-23 — ACCEPTED AS DELIVERED BY THINESH.** No ranking or cap applied. The Declined / Dormant / Never-sold split (1,299 / 3,761 / 3,007) remains available in the data if a sharper queue is wanted later. |
| ~~H~~ | ~~Anchor sits on a partial day~~ | — | **CLOSED 2026-07-22.** The scheduled job anchors on the **last day of the previous calendar month**; ad-hoc runs use the last **complete** day. A second cause was also fixed: **9,222 of 11,176 rows tie** on (priority, 90-day sales, stock) and the listings SELECT has no ORDER BY, so identical data came out in a different order each run — `item_id` is now the final sort key. Two consecutive runs now produce a byte-identical payload (`cdcc3d58…`). |
| **G** | Confirm **Rule 8's £5.00 / 30-day** spend threshold. | Thinesh | Invented for the build because the source defines "high" nowhere. Currently drives only 2 listings, but it is unvalidated. |

## Reviewer gates

- **Sajeesan (technical)** — ⬜ pending
- **Tamil Selvan (queryability)** — ⬜ pending
- **Thinesh (business)** — ✅ **VERIFIED 2026-07-23.** Dashboard accepted, and decisions **C** (rule precedence, incl. Rule 10 staying shadowed) and **F** (72.2% single action accepted as delivered) **explicitly confirmed closed**.
- **Varmen (coordination / ID approval)** — ⬜ pending

## Register links

- Task index: `TASK_REGISTER.md`
- Full functional detail: `SYSTEM_REFERENCE.md`
- Execution rules: `CLAUDE.md`
- Portfolio row: `../../PROJECT_REGISTER.md` — ⬜ not yet added
- Data audit (key evidence):
  `evidence/logs_or_screenshots/REQ-16_ebay-slow-no-moving-products/2026-07-22_data_availability_audit.md`

## Next action

1. **Confirm `PRJ-2026-014` / `REQ-16` / code `esnm`**, then add the `PROJECT_REGISTER.md` row.
2. Write the independent verification record under `validation/REQ-16_.../`.
3. Close decisions **A**, **C** and **F** — all three change *what the report says*, not merely how
   it looks.
4. Only then consider D02 (HTML dashboard) and D03 (scheduled refresh).
