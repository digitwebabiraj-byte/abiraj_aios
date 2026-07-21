# Decision C — "Units in stock" for a multi-variant listing

## ✅ ANSWERED 2026-07-21 — **OPTION A (SUM across variants)**

A listing counts as out of stock only when **every one of its versions is at zero**. This is what the
delivered report already does, so **nothing was rebuilt** — the 15 recommendations stand unchanged.

Decisive evidence at campaign grain (31 live campaigns):

| Definition | Campaigns flagged by the Stock rule |
|---|---|
| **A — every version at zero (CHOSEN)** | **8 of 31** |
| B — any one version at zero | **31 of 31 — every live campaign** |

Option B would have paused the entire live account, which is why this was a confirmation rather than
a genuine choice.

### The rule, stated as a worked example (confirmed 2026-07-21)

Listing "Ceiling Light" with three versions:

| Version | Stock |
|---|---|
| White | 12 |
| Black | **0** |
| Grey | 5 |

→ **NOT out of stock.** The campaign keeps advertising, because White and Grey still have stock.
The listing only counts as out of stock when **all three** are at 0.

**Accepted caveat:** if Black were the best seller, the campaign keeps paying for ads on a version
nobody can buy. Meshika accepted this 2026-07-21 in preference to Option B, which would have flagged
every live campaign. The limitation is stated on the report.

---


**Prepared:** 2026-07-21 · read-only, raw `ledsone` DB
**For:** **Meshika** (Business Validator) + Sajeesan (technical)
**Question:** 89.2% of advertised listings map to more than one SKU (max 245). When the pause engine
asks "how many units does this listing have?", which number does it use?

**Scope of the run:** LEDSone eBay UK, ON_SITE campaigns with `campaign_status='RUNNING'`,
30D window to 2026-07-21, 888 advertised listings (730 resolvable + 158 with no listing record).
Grain = one row per listing.

---

## Finding 1 — there are only TWO options, not three

"MIN across variants" and "ANY variant below the floor" are **mathematically the same rule**:
`MIN(units) < 5` is true exactly when at least one variant is below 5. They produce identical
results (301 pauses each). The decision is **binary**.

---

## Finding 2 — the two options are 9× apart

| Definition | Stock pauses | Rule 1 | Rule 2 | **Total pauses** | Keep running | No data | 30D spend paused |
|---|---|---|---|---|---|---|---|
| **A. SUM across variants** | 14 | 5 | 14 | **33** | 696 | 159 | **£296.87** |
| **B. MIN / ANY-below-floor** | 292 | 1 | 8 | **301** | 428 | 159 | **£1,549.83** |

Total 30D ON_SITE running spend across these listings ≈ £1,846.

- **A pauses 4.5% of listings and 16% of spend.**
- **B pauses 41% of listings and 84% of spend.**

---

## Reading the result

**B is not a stock-protection rule — it is a catalogue shutdown.** With up to 245 variants on one
listing, the probability that *at least one* variant sits below 5 units approaches certainty for any
large listing. So B pauses the biggest, most-stocked, best-selling listings precisely *because* they
are big. Note the tell in the table: under B, Rule 1 pauses collapse from 5 to 1 and Rule 2 from 14
to 8 — not because those listings improved, but because the stock gate now fires first and swallows
them. The engine stops being an efficiency tool.

**A is the permissive end.** A listing whose top-selling variant is at zero still looks healthy if
its siblings carry stock, so A will miss some genuine "advertising something unbuyable" cases. That
is a real cost, but a bounded one.

**Recommendation: A (SUM), for V1** — with the caveat stated on the report that per-variant
stock-outs are not detected. It keeps the engine's purpose intact (catch waste), where B would
inflict a large, indiscriminate spend cut that no one asked for.

**Better, if the business wants it later:** stock of the *advertised* variant only. Not available
today — `ads` target the listing (`ebay_listing_id`), not the variation, so the data cannot say
which variant the ad money went to. This would need a new source, not a new rule.

---

## What is NOT affected by this decision

- **159 listings (17.8%) have no listing record at all** → NO DATA under every definition. They are
  never auto-paused. Unchanged by C.
- Rule 1 and Rule 2 logic itself.
- The 5-unit floor value (that is decision G).

---

## Asked of the validator

1. **A or B?** (recommendation: **A**)
2. If A: confirm it is acceptable that a listing with one dead variant keeps advertising.
3. If B: confirm that pausing ~41% of live listings and 84% of ON_SITE spend is intended.

Query and full method: `../../sql/REQ-15_ebay-ppc-product-pause-automation/` and
`../../evidence/logs_or_screenshots/REQ-15_.../2026-07-21_field_by_field_source_verification.md`.
