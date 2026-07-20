# Live count verification — REQ-14_ebay-return-analysis (2026-07-20)

**Method:** direct **psycopg2** connection to the live **`ledsone`** database (host `207.148.78.148:5432`,
user `dbhub_readonly`, **read-only session**) — **NO MCP**. Ran the canonical
`sql/REQ-14_.../ebay_return_analysis.sql` verbatim: statement 1 wrapped in an aggregate subquery for the
headline totals, statement 2 run as-is for the reason breakdown. Reporting window June 2026
(`2026-06-01`→`2026-07-01`), unchanged from the handoff. Server: PostgreSQL 18.4.

## Result — every headline reproduces the reference EXACTLY
| Metric | Live (`ledsone`, direct) | Reference xlsx | Match |
|---|---|---|---|
| SKU rows | **144** | 144 | ✅ |
| Returns | **153** | 153 | ✅ |
| Orders (period units) | **863** | — (not a totalled column in the ref) | — |
| Blended Return Rate | **0.1773 (17.7%)** | 17.7% | ✅ |
| Refund (£) | **£2,937.37** | £2,937.37 | ✅ |
| Return Cost (£) | **£869.39** | £869.39 | ✅ |
| Ad Spend (£) | **£1,387.96** | £1,387.96 | ✅ |
| Ad Sales (£) | **£9,343.63** | £9,343.63 | ✅ |
| ACOS (derived) | **0.1485 (14.9%)** | 14.9% | ✅ |
| ROAS (derived) | **6.73x** | 6.73x | ✅ |

## Reason breakdown (statement 2) — sums to 153 ✅
Wrong Size 47 (30.7%) · Ordered Wrong Item 28 (18.3%) · Not as Described 21 (13.7%) · No Longer Needed 17
(11.1%) · Ordered Different Item 11 (7.2%) · Defective Item 11 (7.2%) · Ordered Accidentally 8 (5.2%) ·
Arrived Damaged 4 (2.6%) · No Reason Given 2 (1.3%) · Buyer No-Show 2 (1.3%) · Withdrawn from Purchase 2
(1.3%) → **TOTAL 153**. Matches the handoff's stated top reasons (Wrong Size 47 / Ordered Wrong Item 28 /
Not as Described 21 / …).

## Conclusion
The canonical SQL, executed **live** today against `ledsone` via a direct read-only connection, reproduces
the June-2026 reference build **to the penny on every headline** and the reason breakdown to the unit. The
query is confirmed correct against current live data.

## Still pending (not done here)
- Full workbook rebuild (`main.tsv` + `reason_breakdown.tsv` → `build_dashboard.py` → LibreOffice recalc)
  and a row-level diff of all 144 rows (only aggregate totals + reason breakdown were checked here).
- Owner confirmation of the `REQ-14` / `ERA` identifiers.
- Reviewer (Sajeesan, Tamil Selvan) + business (Thinesh) sign-off.
- Any publish to `tech_team_outputs.ph_task` (none done).

**No writes of any kind were issued** — read-only session; source data untouched.
