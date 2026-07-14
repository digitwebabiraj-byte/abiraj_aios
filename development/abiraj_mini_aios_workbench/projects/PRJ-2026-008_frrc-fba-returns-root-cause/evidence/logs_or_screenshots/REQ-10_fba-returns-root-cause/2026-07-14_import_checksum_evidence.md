# Evidence — FRRC REQ-10-D01 import + dataset integrity (2026-07-14)

## 1. Import (COPY-only) — SHA-256 recomputed after copy
```
a48b6af8473f8b38453dfad7ce90a042619f6dbc8e96238a51ab86b9483ed486  HANDOFF_FRRC_REQ-10-D01.md
adaba09886a30e6cb1da64e90a1fde1371f3d8b9e7ffef70ef8c90b55570e2e4  2026-07-14_abiraj_REQ-frrc_REQ-10-D01.md
aae4ab0c42f9f897f7a31624709c3a99ab07b98272aafe8d79bd80ed4fb978b5  FRRC_REQ-10-D01_execution_prompt.md
2cbfe13d0a5e6451498150d05eaab0cf94c2dfb1b0be85658b672edc2f35cbca  frrc30.json
b50ac6968d9eb6db21175c3ef392654e3c06c843423ba0045d8581ea3da9c541  build_frrc30.py
e13adc841c223b2247a58e991cd08fb6452b05c06458d17321a7c4f1e04bad0f  build_console.py
```
6/6 files copied byte-for-byte from `C:\Users\digit\Downloads\files (5).zip`. Originals preserved.

## 2. Dataset integrity re-check (independent, at import)
Re-ran the control assertions on the imported `frrc30.json`:

| Check | Expected (handoff) | Observed | Result |
|---|---|---|---|
| Returning ASIN rows | 91 | 91 | PASS |
| Total return units (Σ total_returns) | 105 | 105 | PASS |
| Per-row bucket sum = total_returns | 0 failures | 0 failures | PASS |
| Flag distribution | — | CRITICAL 44 · HIGH 20 · OK 9 · N/A 18 | recorded |
| N/A (units_sold = 0) | 18 | 18 | PASS |
| Named owners / unassigned | — | 19 named · 18 unassigned | recorded |

Note: N/A count (18) equals the unassigned-owner count (18) — the same rows (returned in-window but
no in-window FBA-UK Completed sale), consistent with the handoff (§4 Responsible Person, §9 open item).

## 3. Scope of this session
Documentation / onboarding only. **No SQL executed** against the live DB in this session — the
dataset was delivered pre-executed and validated by the prior build session; integrity was
re-verified from the file. No DB write, no DDL, no publish, no commit/push.
