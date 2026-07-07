# LEDsONE Centralizer — User Guide

### Business Logic Operating System (BLOS) · Project Sentinel

**Prepared for:** Managing Director and department leaders
**Author:** J. Abiraj
**Date:** 7 July 2026
**Classification:** Confidential — Internal Distribution Only
**System:** LEDsONE Centralizer · live at centralizer.vintageinterior.co.uk

---

## Executive Summary

LEDsONE Centralizer is the company's central operations hub for **governing the business rules
and threshold values that drive day-to-day decisions** across the business. Instead of key
numbers — margin bands, fulfilment limits, pricing floors, PPC targets — living in scattered
spreadsheets and individual memories, the Centralizer holds them in **one governed system**
where every value has a clear owner, a full change history, and a single trustworthy source
that both staff and downstream systems read from.

In short, it answers a question every growing business struggles with:
**"What are our official operating numbers right now, who is allowed to change each one, and
what changed, when, by whom, and why?"**

This guide explains what the system is for, who uses it, how the main tasks are performed, and
what it delivers — so any new user, department leader, or reviewer can understand and operate
it without a personal handover.

---

## 1. Purpose

LEDsONE Centralizer brings four capabilities together in one secure web application:

1. **Threshold Governance** — a managed register of the numeric values ("thresholds") that the
   business rules depend on, each with an owner, a category, a change history, and versioning.
2. **Rule Authoring** — a visual, drag-and-drop Rule Builder where administrators compose the
   logic of a business rule (for example, *"if this metric falls below this threshold, take
   this action"*).
3. **Central File Library** — an organised, searchable store for the company's internal
   knowledge and skill files, with folders, previews, and downloads.
4. **Access Governance** — role-based and domain-based access so each person sees and edits
   only what belongs to their area of responsibility.

Together these turn informal, tribal business knowledge into a **structured, auditable,
single source of truth**.

---

## 2. The Business Problem It Solves

Before a system like this, operating numbers tend to drift: the same figure appears in three
places with three values, nobody is sure which is current, and there is no record of who
changed what or why. That creates risk in pricing, fulfilment, and advertising decisions, and
it makes onboarding and audits painful.

The Centralizer removes that risk by making every threshold a **governed record**:

- **One current value** per threshold, owned by a named business area.
- **A complete history** — every change keeps the old value, the new value, the person, the
  time, and the reason.
- **Controlled editing** — only the right people can change the values in their domain.
- **Machine-readable exports** — other systems can read the official values directly, so
  numbers are never hard-coded or copied by hand.

The result is confidence: leadership can see, at any moment, the authoritative set of operating
numbers and the full story behind each one.

---

## 3. Who Uses It — User Roles

| Role | Who they are | What they can do |
|---|---|---|
| **Administrator** | System owners / senior operators | Full control: manage all business rules, thresholds, the glossary, and mappings; author rule logic in the Rule Builder; manage users and domain access; export the full registry; run bulk imports; manage the File Library |
| **Domain Owner** | Department / area leaders | View and update the threshold values **within their own business domains**; view the change history; use the File Library |
| **Standard User** | General staff | Sign in, view the dashboards and the thresholds relevant to them, and browse, preview and download from the File Library |

Access is **scoped by business domain**: a domain owner sees and edits only the thresholds for
the areas assigned to them, while an administrator sees everything. This keeps each team
focused on — and accountable for — its own numbers.

---

## 4. Main Modules

| Module | What it is for |
|---|---|
| **Dashboard** | The role-aware landing workspace — the starting point after signing in |
| **Threshold Configurator** | The main administration surface for the business rules, thresholds, glossary, mappings, version history, exports, and bulk imports |
| **Business OS** | A domain-grouped view of the threshold registry for reviewing and updating values by business area |
| **Rule Builder** | The drag-and-drop workspace (administrators only) where the logic of a business rule is composed and validated |
| **File Manager** | The Central File Library — hierarchical folders, in-browser previews, and file or whole-folder downloads |

---

## 5. How the Work Gets Done — Main Workflows

**Signing in.** A user signs in with their email and password and lands on the Dashboard. Each
person sees only the areas and controls appropriate to their role.

**Reviewing thresholds.** From the Threshold Configurator or the Business OS view, a user sees
the current thresholds for their domains — each with its value, unit, category, and the date
and person of the last change.

**Changing a threshold value.** The owner opens the threshold, enters the new value, records a
reason for the change, and saves. The system automatically stamps the change with the person,
the time, and the previous value, and adds a new entry to that threshold's permanent history —
so nothing is ever silently overwritten.

**Reviewing history.** For any threshold, the full version history is available: every change,
in order, with the old and new value, who made it, when, and why.

**Authoring a business rule.** An administrator opens the Rule Builder, selects a rule, and
visually assembles its logic from the available metrics, operators, and thresholds. The system
validates that every referenced item exists, so rules can only be built from real, registered
values.

**Loading data in bulk.** Administrators can import a prepared spreadsheet (CSV) into any of the
registry tables. The system validates every row and reports any problems, so imports are safe
and predictable.

**Exporting the registry.** The full set of current values can be exported in a machine-readable
format (YAML) for other systems to consume, or as CSV spreadsheets for reporting and review.

**Using the File Library.** Users navigate the folder tree, preview documents in the browser,
and download a single file or an entire folder as a ZIP archive. Administrators additionally
manage the folders and files — uploading, replacing, renaming, moving, and organising content.

**Managing access.** Administrators create users and grant each one access to the business
domains they are responsible for; a user's view updates accordingly.

---

## 6. Inputs and Outputs

| The user provides | The system delivers |
|---|---|
| Sign-in credentials | A secure working session appropriate to the user's role |
| A new threshold value and the reason for the change | The updated value, an automatic record of who/when/old value, and a permanent history entry |
| Business rules, logic, glossary terms and mappings (via forms) | Validated, consistently formatted registry records |
| A prepared spreadsheet (bulk import) | Validated records loaded in one operation, with clear per-row feedback |
| Export requests | The official value set as a YAML file (for systems) or CSV spreadsheets (for people) |
| Uploaded documents (File Library) | Organised, previewable, downloadable knowledge files |

---

## 7. Built-in Governance and Controls

These behaviours are built into the system and protect the integrity of the data:

- **Complete change history.** Every value change is recorded permanently with the old value,
  new value, person, time, and reason. History is never lost through normal editing.
- **Automatic versioning.** Each change advances the threshold's version number in order, so the
  sequence of changes is always clear.
- **Domain-scoped editing.** Owners can only change values within their assigned business areas.
- **Consistent identifiers.** Business rules, thresholds, glossary terms, and mappings use
  clear, standardised codes, kept consistent automatically.
- **Validated rule logic.** Rules can only reference metrics and thresholds that actually exist
  in the registry, preventing broken or meaningless logic.
- **Safe file replacement.** When a document is replaced, the system shows a before-and-after
  comparison and only commits the change on explicit confirmation.
- **Single source of truth.** Official values are read from the system's exports and interface —
  not copied or hard-coded elsewhere.

---

## 8. Common Tasks — Quick Reference

| I want to… | How |
|---|---|
| See my area's thresholds | Open **Threshold Configurator** or **Business OS** — you see the domains assigned to you |
| Change a value | Open the threshold → enter the new value → record the reason → Save |
| See who changed a value and why | Open the threshold's **version history** |
| Export the current values | (Admin) **Export YAML** for systems, or **Export CSV** for spreadsheets |
| Load many records at once | (Admin) Prepare the CSV → **Bulk import** → review the validation feedback |
| Find and read a knowledge file | Open **File Manager** → browse the folders → click to preview → download if needed |
| Give a colleague access to a domain | (Admin) **Domain Access** → add the person to the domain |

---

## 9. What the System Produces

- A **governed threshold registry** — the authoritative operating numbers, each owned and
  versioned.
- A **complete audit trail** — the full history of every change, ready for review or audit.
- **Machine-readable exports** (YAML) so connected systems always read the current, official
  values.
- **Spreadsheet exports** (CSV) for management review and reporting.
- A **central knowledge library** — the company's internal skill and reference files in one
  organised, accessible place.

---

## 10. Current Status

The core platform is **live and in daily use** at centralizer.vintageinterior.co.uk. The
threshold governance, Rule Builder, Business OS, File Library, and access-control capabilities
described in this guide are all operational. Ongoing work continues to broaden the registered
rule set and to extend documentation and operational guidance to full enterprise standard.

---

## 11. Ownership and Review

| Role | Name |
|---|---|
| Owner / Developer | J. Abiraj |
| Coordinator | Varmen |
| Technical Reviewer | Sajeesan |
| Queryability Reviewer | Tamil Selvan |

---

*LEDsONE Centralizer — User Guide · Project Sentinel · Confidential — Internal Distribution Only*
*Prepared 7 July 2026 by J. Abiraj*
