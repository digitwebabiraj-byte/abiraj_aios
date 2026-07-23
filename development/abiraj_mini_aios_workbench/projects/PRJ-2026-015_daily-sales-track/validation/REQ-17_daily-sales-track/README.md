# Validation — REQ-17 Daily Sales Track

**Status: EMPTY. Nothing to validate — D01 is not built.**

## What lands here

`verify_dst_d01.py` — a re-runnable harness that re-derives every published figure from the live
databases **without importing the builder**, plus a dated verification record.

This is the method that found **6 defects in REQ-16** (two material) and the partial-day anchor
defect in REQ-15. It is not optional.

## What it must check

The 12 PASS/FAIL rules in `TASK_REGISTER.md`, and in particular:

| Check | Why |
|---|---|
| **Reconcile against REQ-13's own query** for an overlapping period | Proves the inherited definitions were actually inherited, not quietly re-derived. This is the duplicate-truth guard. |
| **Two consecutive runs on the same anchor produce an identical payload** | Catches both the partial-day drift and non-deterministic row ordering — REQ-16 hit both. |
| **Every one of the 22 columns is either sourced or visibly blank** | No column may ship silently empty, least of all the six AH/PH columns. |
| **Absent data renders blank, never zero** | A `0` is indistinguishable from a real trading collapse, and detecting collapses is this report's entire purpose. |
| **The 32 verified sample formula relationships hold** | The one part of the spec that is confirmed. |
| **One account-day reconciled by hand** to a figure Thinesh can verify independently | REQ-13 was corrected five times precisely because early passes skipped this. |
