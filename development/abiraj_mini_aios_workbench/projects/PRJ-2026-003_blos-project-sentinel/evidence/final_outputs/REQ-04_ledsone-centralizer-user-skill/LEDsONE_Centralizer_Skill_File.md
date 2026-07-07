# LEDsONE CENTRALIZER (BLOS) — SKILL FILE

**Author: J. Abiraj — Digitweb**
**Created: July 2026 | Version 1.0 | centralizer.vintageinterior.co.uk**
**All content researched and written by J. Abiraj through direct codebase analysis.**

---

## SYSTEM OVERVIEW

LEDsONE Centralizer is the company's central operations hub for **governing the business rules
and threshold values that drive day-to-day decisions**. Instead of key operating numbers —
margin bands, fulfilment limits, pricing floors, PPC targets — living in scattered spreadsheets
and people's memories, the Centralizer holds them in **one governed system** where every value
has an owner, a full change history, and a single trustworthy source that both staff and
downstream systems read from.

The heart of the system is **BLOS — the Business Logic Operating System**: a registry of
business rules and the numeric thresholds those rules depend on, with visual rule authoring and
an append-only audit trail. A **Central File Library** stores the company's internal knowledge
files alongside it.

**Platform:** centralizer.vintageinterior.co.uk

**What this tool manages:**
- Business rules (`BL-###`) and the logic that drives them
- Thresholds (`TH-###`) — the numeric values the rules gate on, with versioned history
- A glossary of metrics (`GL-###`) and rule↔threshold mappings (`MAP-###`)
- Who can see and change each value (roles + per-domain access)
- A central library of internal knowledge/skill files (folders, previews, downloads)
- Machine-readable exports (YAML / CSV) that other systems and AI agents read

> ⚠ **IMPORTANT — SCOPE RULES**
> - **This tool records and governs values — it does not run the marketplace/PPC operations
>   itself.** Other systems read the official values from here.
> - **Threshold *values* can be edited by their domain owners; the rule structure, glossary,
>   mappings, and access control are administrator-only.**
> - **The Central File Library is read-only for non-admins** — browse, preview and download
>   only. Uploads, replacements and deletions are administrator actions.
> - **Some code in the wider repository (POS, PPC/ETL, inventory) is NOT part of this system**
>   and has no screen here — ignore it when using the Centralizer.

---

## MODULE OVERVIEW

| # | Module | What It Does |
|---|--------|--------------|
| 1 | Login & Session | Sign in, choose "remember me", secure token session |
| 2 | Dashboard | Role-aware landing hub with links into the main tools |
| 3 | Threshold Configurator | The 7-section admin suite for the whole BLOS schema |
| 4 | — Thresholds | View and edit threshold values (the one tab non-admins see) |
| 5 | — Business Rules | Create and manage the `BL-###` rule records |
| 6 | — Condition Logics | View the per-stage rule logic (built in the Rule Builder) |
| 7 | — Rule–Threshold Mappings | Link rules to the thresholds they use |
| 8 | — Glossary | Manage the metric terms (`GL-###`) used in rules |
| 9 | — Versions (Audit Trail) | The permanent history of every threshold value change |
| 10 | — Domain Access Console | Assign which business domains each user can access |
| 11 | Business OS | A friendly, values-only editor grouped by domain, with YAML export |
| 12 | Rule Builder | Visual builder for the WHEN/THEN logic of a business rule (admin) |
| 13 | File Manager | The Central File Library — folders, previews, uploads, ZIP export |
| 14 | Export (YAML / CSV) | Download the official value set for systems and reporting |
| 15 | Bulk Import (CSV) | Load many records at once with validation |
| 16 | Roles & Permissions | How admin / domain owner / standard access differ |

---
---

## PART A — ACCESS & NAVIGATION

> How you sign in, what you land on, and what your role lets you do.

---

## MODULE 1 — LOGIN & SESSION

**What it is:**
The sign-in screen. You enter your email and password, optionally tick "remember me", and the
system gives you a secure working session scoped to your role.

---

### How to get here
```
Open centralizer.vintageinterior.co.uk → the Login screen appears automatically
```

---

### What you see on this page

| Element | What it is |
|---------|-----------|
| Email field | Your account email |
| Password field | Your password, with a show/hide eye toggle |
| Remember me | Tick to stay signed in on this device; leave unticked for this session only |
| Sign in button | Signs you in — shows "Signing in…" while it works |

---

### How to sign in
```
Step 1 → Enter your email
Step 2 → Enter your password (click the eye icon to check it)
Step 3 → Tick "Remember me" if this is your own device
Step 4 → Click Sign in
```

> On success you land on the Dashboard.
> If your details are wrong, a pop-up message explains what to fix.

---

### Important rules for Login

| Rule | Detail |
|------|--------|
| Account must be active | An inactive account cannot sign in — ask an admin |
| "Remember me" choice | Ticked = stay signed in on this device; unticked = only until you close the browser |
| "Forgot password?" | There is no self-service reset in this tool — an admin resets your password |
| Sessions can expire | If your access changes, the next action returns you to Login — just sign in again |

---
---

## MODULE 2 — DASHBOARD

**What it is:**
Your landing workspace after signing in. It greets you by name, shows your access level, and
gives you cards that jump straight into the main tools. What you see is tailored to your role.

---

### How to get here
```
Top navigation → Dashboard   (or it opens automatically after login)
```

---

### What you see on this page

| Region | What it shows |
|--------|---------------|
| Welcome hero | "Welcome back, {your name}" and a line describing what you can do |
| Access chips | Your role label and a "Live workspace" chip |
| Metrics strip | Workspace tools count · your Access level · File library (Full / Read-only) · Threshold scope (Unrestricted / Domain-scoped) |
| Non-admin notice | (Non-admins only) an amber banner explaining your read-only and domain-scoped access |
| Workspace tools | Cards linking to Threshold Configurator, Business OS, and the File Library |

> Administrators also reach the **Rule Builder** from the top navigation (there is no Dashboard
> card for it).

---

### Important rules for Dashboard

| Rule | Detail |
|------|--------|
| Role-aware | Admins and non-admins see different wording, chips and cards |
| No data entry here | The Dashboard is a launch pad — actual work happens in the tools it links to |

---
---

## MODULE 16 — ROLES & PERMISSIONS

**What it is:**
The access model that decides what each person can see and do. Every user has one **role**, and
non-admins are additionally scoped to specific **business domains**.

---

### The three roles

| Role | Who they are | What they can do |
|------|--------------|------------------|
| **Administrator** | System owners / senior operators | Everything: all Threshold Configurator sections, Business Rules, Condition Logics, Glossary, Mappings, Versions, Domain Access; the Rule Builder; exports and bulk imports; full File Library management |
| **Domain Owner** | Department / area leaders | View and **edit threshold values within their assigned domains**; view history; browse/download the File Library |
| **Standard user (Cashier)** | General staff | Sign in, view the thresholds for their domains, browse/preview/download the File Library |

---

### How domain scoping works

- A non-admin sees only the thresholds whose **domain** matches their account domain or the
  extra domains an admin has granted them.
- If a non-admin has **no** domains assigned, they see an on-screen hint explaining that they
  should ask an admin to assign domains — this is expected, not a fault.
- Administrators bypass scoping entirely and see all domains.

---

### Important rules for Roles & Permissions

| Rule | Detail |
|------|--------|
| Admin controls are hidden, not greyed out | Non-admins simply don't see admin buttons, tabs or the Rule Builder link |
| Role is re-checked on every screen change | If your access changes, it takes effect on your next click |
| Rule Builder is admin-only | Both the menu link and the page itself are blocked for non-admins |
| Access changes need an admin | Only administrators grant roles and domain access |

---
---

## QUICK REFERENCE — PART A

### Navigation

| What you want to do | Where to go |
|---------------------|-------------|
| Sign in | centralizer.vintageinterior.co.uk |
| See your workspace | Top nav → Dashboard |
| Manage thresholds & rules | Top nav → Threshold config |
| Edit values by domain | Top nav → Business OS |
| Build rule logic (admin) | Top nav → Rule Builder |
| Open the file library | Top nav → Files |

### Top-navigation links

| Link | Who sees it |
|------|-------------|
| Dashboard | Everyone |
| Threshold config | Everyone (non-admins see the Thresholds section only) |
| Business OS | Everyone (scoped to your domains) |
| Rule Builder | Administrators only |
| Files | Everyone (read-only for non-admins) |

---
*Version 1.0 | Prepared by: J. Abiraj | Date: 2026-07-07*

---
---

## PART B — THRESHOLD GOVERNANCE

> The Threshold Configurator is the master administration suite. It has seven sections down the
> left sidebar, each mapped to one part of the BLOS registry. Non-admins see only the Thresholds
> section; administrators see all seven plus exports and bulk import.

---

## MODULE 3 — THRESHOLD CONFIGURATOR (overview)

**What it is:**
The master data workspace for the whole BLOS configuration. A left "Sections" sidebar switches
between seven tabs; each shows a searchable, filterable table. Administrators can add, edit,
delete, export, and bulk-import; non-admins get a read/edit view of thresholds only.

---

### How to get here
```
Top navigation → Threshold config
```

---

### The seven sections (left sidebar)

| Icon | Section | What it holds |
|------|---------|---------------|
| ◆ | **Thresholds** | The numeric values (`TH-###`) — the default section |
| ◇ | **Business Rules** | The rule records (`BL-###`) |
| ◎ | **Condition Logics** | The per-stage WHEN/THEN logic (built in the Rule Builder) |
| ⛓ | **Rule–Threshold Mappings** | Links between rules and thresholds (`MAP-###`) |
| 📖 | **Glossary** | The metric terms (`GL-###`) |
| ⊕ | **Domain Access** | Which users can access which domains |
| ◷ | **Versions** | The audit trail of every threshold value change |

> **Non-admins:** only the **Thresholds** section is shown; the other six are administrator-only.

---

### Shared page features (all sections)

| Feature | What it does |
|---------|--------------|
| Search box | Free-text search across every column of the table |
| Filters | Per-section filters (e.g. thresholds by domain / status / type) |
| Count pills | A clickable stat per section showing how many records it holds (admin) |
| Add new | Opens the add form for that section (admin) |
| Export CSV / YAML | Downloads the section's data (admin — see Module 14) |
| ⤓ Bulk upload | Imports a CSV into that section (admin — see Module 15) |
| Mobile drawer | On phones, a ☰ button opens the section list |

---

### Important rules for Threshold Configurator

| Rule | Detail |
|------|--------|
| Sections = data tables | Each section is one part of the registry; switching sections clears your search/filters |
| Non-admins see thresholds only | The other six sections are hidden for non-admin roles |
| IDs are auto-generated | New records get the next `TH-/BL-/MAP-/GL-` code automatically (with an unlock option) |
| Condition Logics are not typed here | The Add/Edit buttons open the visual Rule Builder instead |

---
---

## MODULE 4 — THRESHOLDS (view & edit values)

**What it is:**
The core section: the list of every threshold value the business rules depend on. This is the
one section every user can see (scoped to their domains). From here values are viewed, searched,
and edited — and every change is recorded permanently.

---

### How to get here
```
Top nav → Threshold config → Thresholds (default section)
```

---

### How to find a threshold
```
Step 1 → Type any part of the key, label, or value in the search box
Step 2 → Or use the filters: Domain, Status (active/inactive), Type (common/specific)
Step 3 → The table narrows as you search
```

---

### How to change a threshold value
```
Step 1 → Find the threshold row
Step 2 → Click Edit on that row
Step 3 → Change the value
Step 4 → Type the reason for the change in the "why" field
Step 5 → Click Save
```

> When you save, the system automatically records **who** changed it, **when**, the **old**
> value and the **new** value, and adds a permanent entry to the Versions (audit trail). The
> version number increases by one. Nothing is ever silently overwritten.

> ⚠ **Always type a real reason.** The reason box is not currently enforced (Save works even if
> it is empty), so the quality of the audit trail depends on you filling it in.

---

### How to add a new threshold (admin)
```
Step 1 → Click Add new
Step 2 → The ID field is pre-filled with the next TH-### code (locked)
         → click the 🔒 unlock button only if you must set it manually
Step 3 → Fill in the label, value, unit, domain, and other fields
Step 4 → Click Save
```

> The system checks the code format and warns you if a code already exists.

---

### How to delete a threshold (admin)
```
Step 1 → Find the threshold row
Step 2 → Click Delete
Step 3 → Confirm on the "Delete record? This cannot be undone." dialog
```

> ⚠ Deleting a threshold also removes its entire version history and its rule mappings. Treat
> deletion as an approval-required action.

---

### Important rules for Thresholds

| Rule | Detail |
|------|--------|
| Every change is recorded | Person, time, old value, new value and reason go to the audit trail |
| Version auto-increments | Each real change advances the version number by 1 |
| A "no-change" save records nothing | Saving the same value writes no history entry — by design |
| Domain-scoped | Non-admins see and edit only their assigned domains |
| Delete cascades | Deleting a threshold removes its history and mappings too |

---
---

## MODULE 5 — BUSINESS RULES (admin)

**What it is:**
The section listing the business rules themselves (`BL-###`) — the rule records that the
thresholds and logic hang off. Here administrators create and manage the rule entries.

---

### How to get here
```
Top nav → Threshold config → Business Rules
```

---

### How to add a business rule
```
Step 1 → Click Add new
Step 2 → The Rule ID is pre-filled with the next BL-### code
Step 3 → Enter the rule name, description, domain, owner and status
Step 4 → Click Save
```

> The actual WHEN/THEN logic for a rule is built separately in the **Rule Builder** (Module 12),
> not on this form.

---

### Important rules for Business Rules

| Rule | Detail |
|------|--------|
| Admin only | This section is hidden for non-admin roles |
| IDs auto-generate | Next `BL-###` is filled in automatically |
| Logic lives elsewhere | Build a rule's conditions in the Rule Builder |

---
---

## MODULE 6 — CONDITION LOGICS (view only here)

**What it is:**
The section that lists the per-stage logic rows for each rule (for example the *initial*,
*restore*, and *kill* stages). You **view** them here, but you build and edit them in the visual
Rule Builder — never by typing.

---

### How to get here
```
Top nav → Threshold config → Condition Logics
```

---

### How to add or edit condition logic
```
Step 1 → Click "New in Rule Builder" (add) or Edit on a row
Step 2 → The Rule Builder opens with that rule and stage already selected
Step 3 → Build or change the logic visually there (see Module 12)
```

> The Add/Edit buttons deliberately hand off to the Rule Builder so that rule logic is always
> composed visually and stays valid.

---

### Important rules for Condition Logics

| Rule | Detail |
|------|--------|
| Never typed here | Add/Edit always open the Rule Builder |
| Admin only | Hidden for non-admin roles |
| Filter by stage | You can filter rows by stage (initial / restore / kill) |

---
---

## MODULE 7 — RULE–THRESHOLD MAPPINGS (admin)

**What it is:**
The section linking business rules to the thresholds they use (`MAP-###`). It records which
rule depends on which threshold, optionally pointing at the exact logic row.

---

### How to get here
```
Top nav → Threshold config → Rule–Threshold Mappings
```

---

### How to manage mappings
```
Add    → Click Add new → pick the rule and threshold → Save
Delete → Click Delete on a mapping row → confirm
```

> Mapping rows have Add and Delete (there is no separate edit — remove and re-add to change one).

---

### Important rules for Mappings

| Rule | Detail |
|------|--------|
| Admin only | Hidden for non-admin roles |
| Links rules ↔ thresholds | Records the dependency between a rule and a threshold |
| IDs auto-generate | Next `MAP-###` is filled in automatically |

---
---

## MODULE 8 — GLOSSARY (admin)

**What it is:**
The dictionary of metric terms (`GL-###`) — the named measures that rules compare against
thresholds (for example a click-through-rate or a margin percentage). The Rule Builder offers
these terms when you build logic.

---

### How to get here
```
Top nav → Threshold config → Glossary
```

---

### How to manage glossary terms
```
Add  → Click Add new → the next GL-### code is filled in → enter the term and details → Save
Edit → Click Edit on a row → change the details → Save
```

---

### Important rules for Glossary

| Rule | Detail |
|------|--------|
| Admin only | Hidden for non-admin roles |
| Feeds the Rule Builder | Glossary terms appear as the "metric" options when building logic |
| IDs auto-generate | Next `GL-###` is filled in automatically |

---
---

## MODULE 9 — VERSIONS (AUDIT TRAIL)

**What it is:**
The permanent, append-only history of every threshold value change. This is the audit trail
that answers "what changed, when, by whom, from what, to what, and why".

---

### How to get here
```
Top nav → Threshold config → Versions
```

---

### What you see on this page

Each row is one change, showing the threshold, the **old value** (shown in red), the **new
value** (shown in green), who made the change, when, and the reason.

---

### Important rules for Versions

| Rule | Detail |
|------|--------|
| Admin only | Hidden for non-admin roles |
| Grows over time | A new row is added on every real threshold value change |
| The source of truth for history | This is where the reason you typed on a value change is stored |

---
---

## MODULE 10 — DOMAIN ACCESS CONSOLE (admin)

**What it is:**
The administrator console for deciding which **business domains** each user can access, and for
renaming a domain across the whole system.

---

### How to get here
```
Top nav → Threshold config → Domain Access
```

---

### How to give a user access to a domain
```
Step 1 → In the "Domain access" card, pick the user
         → the system loads their current domains
Step 2 → Click "Choose from list" and tick the domains to add
         (or type a custom domain and add it)
Step 3 → Review the domain chips (✕ to remove any)
Step 4 → Click Save access
```

> A user's own account domain is always included automatically — this console adds **extra**
> domains on top.

---

### How to rename a domain (admin)
```
Step 1 → In the "Rename domain" card, pick the old domain
Step 2 → Type the new name
Step 3 → Click the rename button
```

> Renaming updates the thresholds and every user's assignments to match.

---

### What you see in the table

A user matrix: user, name, email, role, and the domains each user can access. Each row has an
Edit button that opens the same assign-domains picker.

---

### Important rules for Domain Access

| Rule | Detail |
|------|--------|
| Admin only | This whole section is administrator-only |
| Account domain always included | The console grants extra domains, never fewer than the home domain |
| Rename is global | Renaming a domain updates thresholds and all user assignments together |

---
---

## MODULE 14 — EXPORT (YAML / CSV)

**What it is:**
The way to get the official values out of the system — a machine-readable YAML file for other
systems and AI agents, or CSV spreadsheets per section for reporting.

---

### How to export
```
YAML → On the Thresholds section, click "Export YAML"
       → downloads rules_registry.yaml (the official value set)
CSV  → On any section (except Domain Access), click "Export CSV"
       → downloads that section's data as a spreadsheet
```

> If a download ever comes back as a web page instead of a file, use the **Export** button on
> the page (not a copied link) so your secure token is sent with the request — the system will
> warn you if this happens.

---

### Important rules for Export

| Rule | Detail |
|------|--------|
| Admin only | Exports are administrator actions |
| YAML = the official feed | `rules_registry.yaml` is the single source other systems read |
| CSV per section | Each section exports its own spreadsheet |

---
---

## MODULE 15 — BULK IMPORT (CSV)

**What it is:**
The way to load many records into a section at once from a spreadsheet, with a safety check
before anything is saved.

---

### How to bulk import
```
Step 1 → On the section, click ⤓ Bulk upload
Step 2 → Download the template (the section's CSV export doubles as the template)
Step 3 → Fill it in Excel — keep the header row; leave auto-generated IDs blank
Step 4 → Choose your file and click "Check file" (validate — nothing is saved yet)
Step 5 → Review the result: how many are ready, how many have errors, per-row messages
Step 6 → When it validates cleanly, click "Import N rows" to commit
```

> Tick "Update existing rows" if you want matching rows updated rather than skipped.

---

### Important rules for Bulk Import

| Rule | Detail |
|------|--------|
| Admin only | Bulk import is an administrator action |
| Validate before commit | The Import button stays disabled until a clean validation exists |
| Per-row feedback | Errors are reported row by row, so nothing fails silently |
| Keep the header row | The template header must stay intact for the import to map columns |

---
---

## QUICK REFERENCE — PART B

### Navigation

| What you want to do | Where to go |
|---------------------|-------------|
| Change a threshold value | Threshold config → Thresholds → Edit |
| See who changed a value | Threshold config → Versions |
| Add a business rule | Threshold config → Business Rules → Add new |
| Manage metric terms | Threshold config → Glossary |
| Assign domains to a user | Threshold config → Domain Access |
| Export the official values | Threshold config → Thresholds → Export YAML |
| Load many records at once | Threshold config → (section) → ⤓ Bulk upload |

### Who can use each section

| Section | Admin | Domain Owner / User |
|---------|-------|---------------------|
| Thresholds | ✓ full | ✓ view/edit own domains |
| Business Rules | ✓ | ✗ |
| Condition Logics | ✓ | ✗ |
| Rule–Threshold Mappings | ✓ | ✗ |
| Glossary | ✓ | ✗ |
| Versions | ✓ | ✗ |
| Domain Access | ✓ | ✗ |

---
*Version 1.0 | Prepared by: J. Abiraj | Date: 2026-07-07*

---
---

## PART C — BUSINESS OS

> A friendlier, values-only way to review and edit thresholds, grouped by business area, with a
> one-click YAML export. Same underlying values as the Threshold Configurator — nicer for
> day-to-day value editing.

---

## MODULE 11 — BUSINESS OS (OIL Configurator)

**What it is:**
A clean editor over the same threshold values, organised **Domain → Channel → Type**, so a
domain owner can review and update their numbers by business area without touching the full
admin grid. It also produces the `rules_registry.yaml` export.

---

### How to get here
```
Top navigation → Business OS
```

---

### What you see on this page

| Region | What it shows |
|--------|---------------|
| Domains sidebar | One button per business domain (with an icon and a count), plus a System → "Export YAML" item |
| Topbar | Counts for Domains / Thresholds / Unsaved, and Save All / Export buttons |
| Value cards | Thresholds grouped by channel and type, each with an editable number field |
| Unsaved badge | Shows how many values you have changed but not yet saved |

---

### How to edit values by domain
```
Step 1 → Click your domain in the left sidebar
Step 2 → Use the search box to find a threshold if needed
Step 3 → Change the number directly in its field
         → changed fields turn amber
Step 4 → Click Save Changes (or Save All)
```

> Every save records an audit reason automatically ("Updated via Business OS Configurator"), so
> your changes still appear in the Versions history.

---

### How to export the registry as YAML
```
Step 1 → Click System → "Export YAML" in the sidebar
Step 2 → Click 📋 Copy YAML or ⬇ Download .yaml
```

> This YAML is the single source of truth read by connected systems and automation. Note it
> includes any unsaved edits you are currently viewing.

---

### Important rules for Business OS

| Rule | Detail |
|------|--------|
| Same values as Threshold Configurator | It edits the same thresholds, just grouped and simplified |
| Changed fields turn amber | Unsaved edits are highlighted; the topbar counts them |
| No leave-warning | If you navigate away with unsaved edits, they are lost — Save first |
| Domain-scoped | Non-admins see only their assigned domains; the server enforces permissions on save |
| Discard button | "Discard" clears your unsaved edits immediately (no confirm dialog) |

---
---

## PART D — RULE AUTHORING

> Where administrators compose the actual logic of a business rule — the WHEN (conditions) and
> THEN (decision) — visually, without typing code.

---

## MODULE 12 — RULE BUILDER (admin)

**What it is:**
The visual workspace for building a rule's logic. You pick a business rule, choose a stage, and
assemble conditions like *"when this metric is less than this threshold, and that metric is at
least that threshold"* using dropdowns — then set the decision. No coding, no typing of rule
strings.

---

### How to get here
```
Top navigation → Rule Builder      (administrators only)
   — or —
Threshold config → Condition Logics → Add/Edit  (opens the Rule Builder on that rule)
```

---

### What you see on this page

| Region | What it shows |
|--------|---------------|
| Business rules sidebar | Every rule (`BL-###` + name), and a ＋ New rule button |
| Stage tabs | One tab per stage (e.g. initial / restore / kill), plus ＋ New |
| WHEN section | The visual condition builder (groups and clauses) |
| Preview | The plain-English sentence and the saved logic, side by side |
| THEN field | The decision/output for the rule |
| "Where this rule applies" | Optional context (level, channel, account, site, owner, etc.) |
| Save bar | Save status, Delete stage, Discard changes, and Save |

---

### How to build a rule's logic
```
Step 1 → Pick the business rule in the left sidebar
         (or click ＋ New rule to create one first)
Step 2 → Pick a stage tab, or click ＋ New for a new stage
Step 3 → Set the Stage name (e.g. initial / restore / kill)
Step 4 → In the WHEN section, add conditions:
           - choose a Metric (from the glossary)
           - choose an Operator (is less than, is at least, etc.)
           - choose a Threshold
Step 5 → Add more conditions; use "Match ALL" (AND) or "ANY" (OR),
         and group conditions into either/or branches if needed
Step 6 → Type the decision in the THEN field
Step 7 → Check the Preview (plain-English sentence)
Step 8 → Click Create condition / Save changes
```

> The Preview shows exactly what the rule says in plain English as you build, so you can confirm
> the logic reads correctly before saving.

---

### How to create a new rule
```
Step 1 → Click ＋ New rule in the sidebar
Step 2 → The Rule ID is pre-filled (next BL-###)
Step 3 → Enter the Rule name (required), Domain, and Owner
Step 4 → Click Create rule → it is selected and ready to build
```

---

### How conditions are organised

- **Match ALL of these (AND)** — every condition must be true.
- **Match ANY of these (OR)** — at least one must be true.
- Conditions can be **grouped** into either/or branches for more complex logic, and reordered
  with the ↑/↓ buttons. (The builder uses buttons, not drag-and-drop.)

---

### Important rules for Rule Builder

| Rule | Detail |
|------|--------|
| Administrators only | The link and the page are blocked for non-admins |
| Metrics and thresholds must exist | You can only build from registered glossary terms and thresholds |
| Unsaved-changes guard | If you try to leave with unsaved edits, a "Discard unsaved changes?" prompt appears |
| Hard refresh still loses edits | The guard covers in-app navigation, not a browser refresh/close — save first |
| Legacy logic is never lost | If a stored rule can't be read visually, a raw-text editor opens so you can fix it |

---
---

## PART E — FILE LIBRARY

> The central store for the company's internal knowledge and skill files. Everyone can browse,
> preview and download; administrators manage the content.

---

## MODULE 13 — FILE MANAGER

**What it is:**
The Central File Library — a folder tree of internal files with in-browser previews, downloads,
ZIP export of whole folders, and (for admins) uploads, replace-with-review, rename, move and
delete. New and updated files are highlighted so you can spot changes.

---

### How to get here
```
Top navigation → Files
```

---

### What you see on this page

| Region | What it shows |
|--------|---------------|
| Library hierarchy sidebar | The folder tree — expand ▸ to browse, click a folder to open it |
| Breadcrumb | Your location (Root → folder → subfolder), each part clickable |
| Contents table | The subfolders and files in the open folder, with "New"/"Updated" badges |
| Toolbar | New folder / Upload (admins), and Reload |
| Row actions | Open, Download, and a "More" menu (admins: Replace, Rename, Move) |

---

### How to find and read a file
```
Step 1 → Expand the folder tree or open a folder
Step 2 → Click a file row to open the viewer
Step 3 → Markdown, text, CSV, JSON and XML files preview in the browser
         (switch between Text and Render views)
```

---

### How to download
```
Single file → Click Download on the file row
Whole folder → Open the folder → click Download (downloads a ZIP of everything inside)
```

---

### How to upload a file (admin)
```
Step 1 → Open the folder you want to upload into
         (uploads must go inside a folder, not the root)
Step 2 → Click Upload file(s) and choose one or more files
Step 3 → The files are stored and appear with a "New" badge
```

---

### How to replace a file with a new version (admin)
```
Step 1 → On the file row, open the More menu → Replace file
Step 2 → Choose the new file
Step 3 → For text files, a before-and-after review opens:
           - Line diff (removed lines red, added lines green)
           - or Rendered view for markdown/JSON/CSV/XML
Step 4 → Click "Replace library file" to confirm (or Cancel to keep the original)
```

> The review step appears for previewable text files up to ~900 KB. Larger or binary files
> replace immediately without a diff.

---

### How to organise files and folders (admin)
```
New folder → Toolbar → New folder → name it → Create
Rename     → More menu → Rename → new name → Save
Move file  → More menu → Move → pick the target folder → Move
Delete     → Delete on the row/folder → confirm the danger dialog
```

> ⚠ Deleting a folder removes **everything inside it** — all nested subfolders and every file,
> from storage and the catalog. This cannot be undone.

---

### Important rules for File Manager

| Rule | Detail |
|------|--------|
| Read-only for non-admins | Non-admins get Open and Download only; all management is admin-only |
| Uploads go inside folders | Nothing is stored loose at the root |
| Replace shows a diff | Text-file replacements are reviewed before they commit |
| New/Updated highlighting | Changed files are badged until you open, download or acknowledge them |
| Folder delete cascades | Deleting a folder deletes all of its contents permanently |
| Press Reload after changes | The library refreshes on Reload if someone else changed it |

---
---

## QUICK REFERENCE — PARTS C · D · E

### Navigation

| What you want to do | Where to go |
|---------------------|-------------|
| Edit values by business area | Business OS → pick domain → edit → Save |
| Export the official YAML | Business OS → Export YAML (or Threshold config → Export YAML) |
| Build a rule's logic | Rule Builder → pick rule → build WHEN/THEN → Save |
| Read an internal file | Files → open folder → click file |
| Download a whole folder | Files → open folder → Download (ZIP) |
| Upload / replace a file (admin) | Files → Upload, or More → Replace file |

### Where the same value can be edited

| Value | Threshold Configurator | Business OS |
|-------|------------------------|-------------|
| Threshold value | ✓ (Thresholds → Edit) | ✓ (domain view) |
| Records an audit reason | You type it | Automatic generic reason |
| Warns before losing unsaved edits | Modal per edit | ✗ (save before leaving) |

---
*Version 1.0 | Prepared by: J. Abiraj | Date: 2026-07-07*

---
---

## APPENDIX — KEY TERMS

| Term | Meaning |
|------|---------|
| **BLOS** | Business Logic Operating System — the rules-and-thresholds core of the Centralizer |
| **Threshold (`TH-###`)** | A numeric value a business rule gates on (e.g. a margin %, an SLA day count) |
| **Business rule (`BL-###`)** | A named rule whose logic and thresholds decide an outcome |
| **Glossary term (`GL-###`)** | A named metric used in rule conditions |
| **Mapping (`MAP-###`)** | A link recording which rule uses which threshold |
| **Condition logic** | The per-stage WHEN/THEN logic of a rule, built in the Rule Builder |
| **Stage** | A phase of a rule's logic (e.g. initial / restore / kill) |
| **Domain** | A business area used to scope who can see and edit which thresholds |
| **Version / audit trail** | The permanent record of every threshold value change |
| **rules_registry.yaml** | The exported official value set that other systems and AI agents read |

---

## APPENDIX — GOLDEN RULES

1. **Always type a real reason when changing a value** — it becomes the permanent audit record.
2. **Save before you leave** — Business OS does not warn you about unsaved edits.
3. **Threshold values are editable by domain owners; rules, glossary, mappings and access are
   admin-only.**
4. **The File Library is read-only unless you are an administrator.**
5. **Deletions cascade** — deleting a threshold removes its history; deleting a folder removes
   everything inside it.
6. **`rules_registry.yaml` is the official feed** — other systems read from it, so keep the
   values correct and current.

---

*LEDsONE Centralizer (BLOS) — Skill File · Version 1.0 · Confidential — Internal Distribution Only*
*Prepared 2026-07-07 by J. Abiraj — Digitweb · Researched through direct codebase analysis*
