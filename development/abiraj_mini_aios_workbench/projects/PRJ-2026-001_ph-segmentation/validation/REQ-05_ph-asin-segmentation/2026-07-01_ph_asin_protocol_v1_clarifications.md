# PH ASIN Segmentation — Protocol v1.0 Clarifications

| Field | Value |
| ----- | ----- |
| project | PH ASIN Segmentation — Growth Protection Engine (GPE) |
| project_code | ph-asin |
| requirement_id | REQ-05 |
| prepared_by | abiraj |
| for_sign_off | Bietrick |
| date | 2026-07-01 |
| status | Awaiting sign-off |

---

## Purpose

The original segmentation protocol defines the six segments, the benchmark method, and the movement logic. In building the engine, four situations came up that the written protocol did **not** explicitly cover. The engine had to make a consistent decision for each so that classification is repeatable and defensible.

This document records those four decisions as **official clarifications** so the behaviour is written down, agreed, and stable. None of these change the six segments or the benchmark method — they only make explicit what happens at the edges. Each is applied identically to every ASIN, every cycle.

---

## Clarification 1 — Lateral move = SAME

**Situation.** Movement is decided by an ASIN's *h-count* (number of HIGH signals: HHH = 3; HHL / HLH / LHH = 2; LLH = 1; LLL = 0). Two different segments can share the same h-count — for example HHL and HLH are both h-count 2. If an ASIN moves from HHL to HLH, its segment label changed but its overall strength did not.

**Rule.** Movement compares **h-count only**. If the previous and current h-count are equal, movement = **SAME**, even if the segment letters changed. A change in *which* signals are high (a lateral shift) is not counted as IMPROVED or DECLINED.

**Why.** Movement is meant to answer "is this product getting stronger or weaker overall?" A sideways change (one strength swapped for another) is neither, so flagging it as improve/decline would be a false signal. The letter change is still visible in the segment itself.

---

## Clarification 2 — Zero clicks → conversion signal = LOW

**Situation.** The conversion signal compares an ASIN's conversion rate (CVR) to the benchmark. If an ASIN received **0 clicks** in the window, CVR is undefined (division by zero) — there is no conversion behaviour to measure.

**Rule.** If clicks = 0, the conversion signal is **LOW**.

**Why.** A product that nobody clicked has not demonstrated any ability to convert, so it cannot be credited a HIGH conversion signal. Treating it as LOW is the conservative, honest reading and keeps un-clicked products from appearing artificially strong.

---

## Clarification 3 — Conversions greater than clicks → conversion signal = HIGH

**Situation.** Occasionally an ASIN shows **more conversions than clicks** in the window. This is normal in the data: a single click can lead to a multi-unit order, and Amazon's attribution can credit a conversion to a session whose click fell in an adjacent period. Mathematically this makes CVR exceed 100%.

**Rule.** If conversions > clicks, the conversion signal is **HIGH** (before the ordinary CVR-vs-benchmark test is applied).

**Why.** More conversions than clicks is the strongest possible conversion evidence — the product is turning attention into sales at an exceptional rate. It would be wrong to let a >100% CVR fall through the normal comparison and risk being mis-scored. This is capped at HIGH by definition.

---

## Clarification 4 — Undefined signal combinations mapped to the nearest segment

**Situation.** Each ASIN gets a three-letter raw code `[Impression][Click][Conversion]`, each H or L — eight possible combinations. The agreed scheme uses **six** named segments. Two raw combinations have no named segment:

- **HLL** — high impressions, low clicks, low conversion
- **LHL** — low impressions, high clicks, low conversion

**Rule.** These two are mapped to the nearest defined segment:

| Raw code | Mapped to | Reading |
| ----- | ----- | ----- |
| HLL | **HLH** | Seen a lot, not clicked/converting → treated as a visibility-rich, engagement-poor case (Wallflower family) |
| LHL | **HHL** | Clicked but not seen widely or converting → treated as a traffic-present, conversion-poor case (Leaky-Bucket family) |

**Why.** Every ASIN must land in exactly one of the six segments. These two mappings send each undefined code to the segment whose action-plan best fits its actual problem, so the recommended fix still makes sense for the product. The mapping is fixed and applied automatically.

---

## Summary

| # | Clarification | Rule |
| ----- | ----- | ----- |
| 1 | Lateral move | Equal h-count → SAME (even if letters change) |
| 2 | Zero clicks | Conversion signal = LOW |
| 3 | Conversions > clicks | Conversion signal = HIGH |
| 4 | Undefined combos | HLL → HLH, LHL → HHL |

These four rules are already implemented consistently in the engine. Once signed off, they become **Protocol v1.0** and will not change without a new agreed clarification.

**Sign-off:**  Bietrick — ☐ Approved  ☐ Changes requested  ______________  (date)
