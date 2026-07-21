# PRJ-2026-013 — eBay PPC Product Pause Automation (EPPA)

**Which LEDSone eBay UK Promoted Listings should stop being advertised right now — because they are
unsellable or losing money — and how much spend does pausing them recover?**

| | |
|---|---|
| Status | **DISCOVERY** — data audit GREEN with 4 gaps; build not started |
| Code | `eppa` · Task `REQ-15_ebay-ppc-product-pause-automation` |
| Scope | LEDSone (`led_sone`) · eBay · **UK** · Promoted Listings |
| Output | Read-only **recommendation** report + staff approve/reject. **Never writes to live PPC.** |
| Opened | 2026-07-21 |

## The rules (first match wins)

| Order | Gate | Pauses when | Rescue |
|---|---|---|---|
| 0 | State | *(campaign OFF → not evaluated at all)* | — |
| 1 | **Stock** | units < 5 | — |
| 2 | **Rule 1** | 30D ACOS ≥ 40% *(needs 30D orders > 0)* | 7D ACOS < 20% = improving |
| 3 | **Rule 2** | 14D clicks ≥ 20 with 0 orders | 14D spend < £2.50 = cheap organic clicks |
| 4 | Custom | user-defined | — |

Priority = High if out of stock, else by 30D spend (≥£40 High, ≥£15 Medium, else Low).

## Live baseline (2026-07-21 dry run, ON_SITE running campaigns)

**21 pause candidates** — 10 stock · 3 Rule 1 · 8 Rule 2 — plus 33 with no stock data, against 678
keep-running. £117 of £1,807 30D spend flagged.

## Where things are

| | |
|---|---|
| Governance, open decisions | [PROJECT_HOME.md](PROJECT_HOME.md) |
| **Full functional detail** | [SYSTEM_REFERENCE.md](SYSTEM_REFERENCE.md) |
| Execution rules | [CLAUDE.md](CLAUDE.md) |
| Task index | [TASK_REGISTER.md](TASK_REGISTER.md) |
| Data audit (the key evidence) | `evidence/logs_or_screenshots/REQ-15_.../2026-07-21_step2_data_availability_audit.md` |
| Live engine query | `sql/REQ-15_.../eppa_rule_engine_dryrun.sql` |
| Sources (COPY, SHA-256) | `evidence/source_documents/REQ-15_.../` |

## Who

Business Validator / end user: **Meshika** (`staff.users` id 182, confirmed 2026-07-21).
Coordinator Varmen · Technical Sajeesan · Queryability Tamil Selvan.

## Open

1. **Decision C — stock grain.** SUM across variants = 33 pauses / £296.87; MIN (= any-variant-below-floor,
   proven the same rule) = 301 pauses / £1,549.83. Built on SUM; needs Meshika's confirmation.
2. **Decision B** — are Standard (COST_PER_SALE) campaigns in scope? They log £0 spend, so neither
   ACOS rule can run.
3. **E2** — who receives the published report? Meshika is not in the `ebay_priors` group.
4. Register the weekly task (needs `eppa_secrets.bat`), and get eyes on the dashboard.
