# Evidence — REQ-11-D01 fanned out to the full `ebay_priors` audience (2026-07-31)

**What changed:** the D01 read-only feedback-triage report (originally published only to Thinesh as
`ph_task` id 257) was published to the remaining five `ebay_priors` members, taking the audience from
**1 → 6 users** — matching every other `ebay_priors` report (`dst`, `epc`, `epd`, `ebpd`, `eppr`, `ERA`,
`esnm`, `eckr`), which all already reach the same six people.

**Owner instruction:** "push to all the other users also" → then "update AIOS and git". Audience addition
only — **no new scope, no new data, no rebuild**. The read-only-slice / BUILD-gated status is unchanged
(see `TASK_REGISTER.md`); this does not touch the DDL gate (I) or the A–F / K–O decision sheet.

## What was done (DB — `order_management_copy`, `tech_team_outputs.ph_task`)

Cloned the live row id 257 five times with `INSERT … SELECT … CROSS JOIN (VALUES …)`, changing **only**
`task_id` + `assigned_user` (and fresh `created_at`/`updated_at`); every other column — including the full
`html_content` dashboard, `description`, `phase_level=1`, `version_level=1`, `version_status='released'`,
`assigned_user_team='ebay_priors'` — is a byte-for-byte copy of id 257. `action_took_by` /
`action_took_date_time` left NULL (unactioned), consistent with id 257 and the other new-user rows.

Exact spellings (`Jarsini`, `kobiga`, `powsteena`, `Sharmilan`, `Sivajitha`) taken from the registry
itself — the same `assigned_user` values those users already carry on the other `ebay_priors` reports
(there is no `staff.users` table on `order_management_copy`). No Jarsini/Jasmini-style collision.

| id | task_id | assigned_user | status |
|---|---|---|---|
| 257 | `ebft_Thinesh_ebay_feedback_triage-V1`   | Thinesh   | released *(original, unchanged)* |
| 530 | `ebft_Jarsini_ebay_feedback_triage-V1`   | Jarsini   | released ✅ new |
| 531 | `ebft_kobiga_ebay_feedback_triage-V1`    | kobiga    | released ✅ new |
| 532 | `ebft_powsteena_ebay_feedback_triage-V1` | powsteena | released ✅ new |
| 533 | `ebft_Sharmilan_ebay_feedback_triage-V1` | Sharmilan | released ✅ new |
| 534 | `ebft_Sivajitha_ebay_feedback_triage-V1` | Sivajitha | released ✅ new |

All six now carry the same report. The `task_id` per-user convention matches the other projects, so if a
runner is ever built for `ebft` it would UPDATE these in place rather than duplicating them.

## Verification

`SELECT id, task_id, assigned_user, version_status FROM tech_team_outputs.ph_task WHERE project_code='ebft'
ORDER BY assigned_user;` returned the six rows above — 5 new + the original, all `released`,
`assigned_user_team='ebay_priors'`.

## Not changed

- No new evidence/output files (the dashboard is identical to id 257's — one canonical copy in
  `evidence/final_outputs/REQ-11_ebay-feedback-triage/`).
- No automation exists for `ebft` (D01 was a one-off read-only pull) — nothing to keep in step.
- No change to the read-only slice's content, the BUILD gates, or the decision sheet.
