# PRJ-2026-014 — eBay Slow Moving & No Moving Products (ESNM)

**Across the LEDSone group's eBay accounts on UK and Germany, which listings are slow moving or not
moving at all — and what should be done with each one?**

| | |
|---|---|
| Status | **REQ-16-D01 BUILT + SELF-VERIFIED 2026-07-22** — read-only, not published, not automated, awaiting sign-off |
| Code | `esnm` · Task `REQ-16_ebay-slow-no-moving-products` |
| Scope | **All active eBay accounts** · **UK + Germany only** · sellable rows (`is_ended=0`, `is_child=0`) |
| Output | Read-only **recommendation** report — 20 columns + a 12-rule action engine. **Never writes to eBay.** |
| Opened | 2026-07-22 |

⚠ **IDs pending owner confirmation** — the source file carries no requirement number. `REQ-16`
continues the eBay sequence REQ-12 (`epc`) → REQ-13 (`ebpd`) → REQ-14 (`ERA`) → REQ-15 (`eppa`).

## The rules (priority order, first match wins)

| Order | Rule | Fires when | Action | Priority |
|---|---|---|---|---|
| 1 | R1 | 90-day sales = 0 | End Listing / Clear Stock | **Critical** |
| 2 | R2 | 30-day = 0 AND stock > 50 | Run Clearance Promotion | High |
| 3 | R3 | 7d = 0, 30d ≤ 2, 90d ≤ 5 | Reduce Price 5–10% | High |
| 4 | R4 | drop > 80% vs same period last year | Review Competitor Pricing | High |
| 5 | R5 | views > 100 AND CVR < 1% | Improve Images & SEO Title | High |
| 6 | R7 | stock > 100 AND 90d < 5 | Bundle with Best Seller | High |
| 7 | R8 | PPC spend > £5/30d AND no sales | Pause PPC Campaign | High |
| 8 | R9 | views < 50 in 30 days | Improve SEO & Promotion | Medium |
| 9 | R10 | age > 180d AND last sale > 90d | Refresh or Relist | Medium |
| 10 | R11 | 30-day ≥ 10 | Maintain Current Strategy | Low |
| 11 | R12 | 7-day sales increasing | Increase Stock & PPC Budget | Low |
| — | **R6** | watchers > 10 AND no 30d sales | *(Send Offer)* | **NEVER FIRES — no data** |

⚠ **Precedence is an assumption** — the source assigns priorities but never states how a listing
matching several rules resolves. This is what makes 8,067 listings read "End Listing".

## Live baseline (2026-07-22 anchor, 11,156 listings)

**8,067 Critical (End Listing, 72.3%)** · 1,210 Clearance · 851 Price Cut · 476 SEO · 149 Bundle ·
42 Competitor Review · 26 Listing Quality · 2 Pause PPC · 109 Maintain · 53 Grow · 171 Monitor.

Scope: **12 accounts · 16 account × marketplace combinations** — UK 7,685 / Germany 3,471.

## ⚠ Read this before touching the build

**This report needs TWO databases and cannot be built from either alone.**

| DB | Supplies | Alone it lacks |
|---|---|---|
| `ledsone` | title, category, image, price, stock, sales, PPC (incl. SMART) | **Views + Conversion** — `traffic_data` isn't in it |
| warehouse `order_management_copy` | Views, Conversion, sales, stock, PPC (90d) | **Product Title — only 8.3% populated** |

## Where things are

| | |
|---|---|
| Governance, open decisions | [PROJECT_HOME.md](PROJECT_HOME.md) |
| **Full functional detail** | [SYSTEM_REFERENCE.md](SYSTEM_REFERENCE.md) |
| Execution rules | [CLAUDE.md](CLAUDE.md) |
| Task index | [TASK_REGISTER.md](TASK_REGISTER.md) |
| Data audit (the key evidence) | `evidence/logs_or_screenshots/REQ-16_.../2026-07-22_data_availability_audit.md` |
| Generator | `sql/REQ-16_.../build_esnm_d01.py` |
| Workbook | `evidence/final_outputs/REQ-16_.../REQ-16-D01_slow_no_moving_products.xlsx` |
| Source (COPY, SHA-256) | `evidence/source_documents/REQ-16_.../` |
| Daily requirement document | `DigitWeb_Works_Abiraj/22_07_2026/2026-07-22_abiraj_REQ-esnm_REQ-16-D01.md` |

## Who

Requester / end user / Business Validator: **Thinesh** (`public."user"` id 63, Active, verified
2026-07-22). Coordinator Varmen · Technical Sajeesan · Queryability Tamil Selvan.

## Open

1. **Decision A — Watchers.** No source in either DB. Drop Rule 6, or hold column 17 blank pending a
   Trading-API ingestion?
2. **Decision C — precedence + Rule 10.** Rule 10 matched **0 of 11,156** because Rule 1 always
   claims those listings first. Revise the rule, or accept it as dead?
3. **Decision F — actionability.** 72.3% of rows carry one Critical action; an 8,067-row flat list
   is not usable as delivered. Rank or cap?
4. **Decision B — traffic backfill.** 11 ingestion days lost; Views understated ~23% over 30 days.
5. Confirm the IDs, then `PROJECT_REGISTER.md`, validation record, and (only then) publish/automate.
