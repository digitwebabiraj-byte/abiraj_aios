## **SKILL FILE VALIDATION REPORT**

**File:** 2026-06-03\_\_abiraj\_\_eod\_\_REQ-03-D01.md **Developer:** Abiraj **Project:** EOD Performance Tracker (eod) **Validated on:** 2026-06-03 **Validator:** Claude — DIGITWEB LK LTD. Skill File Validator v3.0 **Overall Score: 60 / 100 — Requires Revision**

---

### **PART 1 — FORMAT AND TEMPLATE COMPLIANCE**

**File Naming Standard — Pass** The filename is correctly structured. Date, developer name, project code, and deliverable ID are all present and properly separated with double underscores. Everything is lowercase. No naming issues found.

**Section Structure — Fail** This is the biggest problem in the file. The v3.0 template requires nine sections with exact names. Abiraj has used the correct section numbers (1 through 9\) but has replaced five of the section names with custom titles. Only four sections have the correct mandatory names: Section 1, Section 2, Section 8, and Section 9\.

Here is what went wrong with sections 3 to 7:

Section 3 is titled "Last Date Data" — it should be "POSTGRESQL / MCP FINDING." Instead of documenting database schema changes or MCP queries made today, this section shows a table of tasks logged on April 24\. That is data reporting, not a database finding.

Section 4 is titled "Cumulative Performance Summary" — it should be "GAP FOUND." The gap register is the most important operational section and it is completely missing. Instead, this section contains KPI tables and staff performance numbers. Useful data, but it is in the wrong place and the wrong format.

Section 5 is titled "Issues & Alerts" — it should be "VALIDATION RULE ADDED OR CHANGED." The validation rules that exist in this file are buried in Section 8, not documented here with rule IDs or BLOS references.

Section 6 is titled "Waste Log" — it should be "FAILURE MODE OR EDGE CASE." The waste log shows which tasks were blocked and by what. That is related, but it is not a failure mode analysis. A proper failure mode section explains how to detect the failure and how to recover from it. This section does neither.

Section 7 is titled "Open Items" — it should be "DECISIONS MADE TODAY." No decisions are documented anywhere in this file. The open items list is a task checklist, not a record of why design choices were made.

The reason this matters: the company knowledge system compiles files by searching for exact section names. A section titled "Open Items" will never be found when the system looks for "DECISIONS MADE TODAY." The knowledge in those five sections is effectively invisible to the LLM compilation pipeline.

**Metadata Block — Partial Pass** Thirteen of the fifteen required fields are correctly present. The developer name, project, phase, status, evidence location, three\_am\_standard, llm\_queryable, company\_knowledge\_candidate, and domain are all correctly filled in.

Two mandatory fields are entirely missing. The first is blos\_keys\_used — this must either list the BLOS keys referenced today or state NONE. The second is hardcoded\_thresholds — this must either list all hardcoded threshold values in the file or state NONE. Both fields are absent. Under Rule 5, missing BLOS governance fields is a rejection condition.

There is a second metadata problem. Abiraj has added six extra fields that do not belong in the metadata block: data\_range, total\_tasks\_logged, total\_hours\_logged, verification\_rate, high\_value\_pct, and waste\_hours. These are data reporting numbers, not governance metadata. They belong inside Section 1 or Section 4 content. Putting reporting numbers in the metadata block confuses the LLM compilation pipeline which expects only the fifteen canonical fields.

**Evidence — Partial Pass** The evidence\_location field correctly points to the daily\_eod\_log table in the PostgreSQL ROI database at vintageinterior.co.uk. Any data claim in the file — row counts, staff counts, verified percentages — can be verified by querying that table. That is good practice.

However Section 2 documents five changes made today, and none of them have traceable evidence. The correction to sql\_generate\_skill.md has no Git commit hash and no file path. The Piranav documentation update has no commit reference. The TECH department addition has no commit. The dashboard artifact has no artifact ID or published URL. These five changes are claims with no proof. Rule 7 requires every claim to reference evidence.

**Three-Am Standard — Partial Pass** The developer self-declares PASS and the Section 9 assessment is detailed and honest. A developer arriving with no context would understand what the EOD system does, how to query it correctly, why some queries were returning wrong numbers, and who has verification problems. The plain-language explanations in Section 2 are genuinely good — every technical change is followed by a plain English sentence explaining what it means for the business.

However the Three-Am Standard fails on recovery. There are no recovery steps documented anywhere. If the Step 0 live query breaks, a developer does not know what to do. If the dashboard artifact stops working, there is no repair path. If a LEFT JOIN on ph\_master produces unexpected results after a schema change, there is no diagnostic guidance. The self-assessment says PASS but this dimension was missed.

**Credentials — Pass** No passwords, API keys, tokens, or server IP addresses are present. The database reference is limited to a domain name and table name, which is acceptable. No escalation required.

---

### **PART 2 — SCORING**

| Area | Score | Out of | Reason |
| ----- | ----- | ----- | ----- |
| Metadata Completeness | 7 | 10 | 2 mandatory fields missing. 6 non-standard fields added to metadata block. |
| Structure Compliance | 4 | 10 | Only 4 of 9 section names are correct. 5 sections have custom names that break LLM compilation. |
| Business Logic Clarity | 16 | 20 | Section 8 is precise and implementable. Plain-language explanations in Section 2 are excellent. Deduction for sections 4 and 6 being data reports rather than knowledge extracts. |
| Validation Rule Quality | 5 | 15 | No Section 5 exists. Rules are present in Section 8 but have no rule IDs, no BLOS references, and cannot be retrieved as validation rules by the compilation system. |
| Gap Identification | 5 | 10 | Gap content exists in Sections 5 and 7 but no dedicated GAP FOUND section. No blocking status for any gap. Most open items have no owner assigned. |
| Edge Case Documentation | 6 | 10 | Issues & Alerts section is specific and data-backed. Waste log is detailed. No recovery steps for any failure scenario. |
| Evidence Referencing | 6 | 10 | DB reference covers data claims well. Zero commit evidence for all 5 changes made today. Dashboard build has no artifact reference. |
| LLM Queryability | 11 | 15 | Section 8 and Section 9 are highly queryable and well-structured. 5 mislabelled sections reduce effective retrieval surface to 4 of 9 sections. |
| **Total** | **60** | **100** |  |

---

### **PART 3 — GAPS FOUND — FORMAT AND CONTEXT**

**FORMAT-GAP-01 · Five section names are wrong** Sections 3 through 7 all have the correct numbers but wrong names. The correct names are: Section 3 — POSTGRESQL / MCP FINDING, Section 4 — GAP FOUND, Section 5 — VALIDATION RULE ADDED OR CHANGED, Section 6 — FAILURE MODE OR EDGE CASE, Section 7 — DECISIONS MADE TODAY. The fix is simple: rename the five headings. The content inside mostly does not need to change — only the labels.

**FORMAT-GAP-02 · blos\_keys\_used and hardcoded\_thresholds both absent from metadata** These two fields are mandatory under Rule 5\. They were simply not included. If no BLOS keys were used today, the field should state NONE. If no thresholds are hardcoded, the field should state NONE. Absence means the file fails BLOS governance compliance.

**FORMAT-GAP-03 · No GAP FOUND section with proper structure** Section 4 is a performance dashboard. The mandatory GAP FOUND section does not exist. Every gap must state three things: what is missing, whether it is blocking progress (YES / NO / PARTIAL), and who owns fixing it. The open items in Section 7 do not follow this structure — most have no owner and none have a blocking status.

**FORMAT-GAP-04 · No validation rules documented in Section 5** Section 5 does not exist under the correct name. The validation rules in Section 8 — such as the bigint comparison rule, the TRIM rule, the LEFT JOIN ph\_master rule, and the GBP currency filter rule — are real, implementable rules that should be in Section 5 with rule IDs and BLOS references. They are currently embedded in a bullet list in Section 8 and will not be retrieved when the system queries for validation rules.

**FORMAT-GAP-05 · No decisions documented in Section 7** Section 7 contains a checklist of open tasks. No decisions are recorded. At minimum, the decision to replace hardcoded values with a live Step 0 query is a significant design decision that should be documented here with the reason it was chosen and the risk it creates if the database connection is unavailable.

**FORMAT-GAP-06 · No Git commit evidence for any of the five changes in Section 2** Five changes were made today. Not one of them has a Git commit hash, a file path, or any traceable evidence reference. Rule 7 requires every claim to reference evidence. Five unverifiable changes in a single file is a significant evidence gap.

**FORMAT-GAP-07 · Six non-standard fields polluting the metadata block** data\_range, total\_tasks\_logged, total\_hours\_logged, verification\_rate, high\_value\_pct, and waste\_hours are reporting numbers, not governance metadata. They should be moved to Section 1 content. Leaving them in the metadata block creates false hits when the LLM compilation pipeline filters files by canonical metadata fields.

**FORMAT-GAP-08 · Section 9 self-assessment declares metadata complete — it is not** The Section 9 LLM Standard Check table states "Is metadata complete? YES." This is incorrect. Two mandatory fields are missing and six non-standard fields are present. The self-assessment should have caught this.

---

### **PART 4 — ADDITIONAL GAPS IDENTIFIED BY VALIDATOR**

**VALIDATOR-GAP-001 · SEO verification failure has no owner and no deadline** Four SEO staff have verification rates of 0% to 17%. This is flagged as critical in Section 5\. However no owner is assigned to resolve it and no deadline is set. A critical finding with no owner and no deadline will remain unresolved indefinitely. Someone must be named as responsible and a date must be set.

**VALIDATOR-GAP-002 · 40-day data gap has no upload owner** May and June 2026 EOD data has not been uploaded. The open item in Section 7 says "upload May and June EOD CSV files" but does not say who is responsible for uploading them. Without an owner, this gap has no resolution path.

**VALIDATOR-GAP-003 · ph\_master.band standardisation has no owner and no timeline** The band values in ph\_master (Senior, Junior, Probationer) do not match the A–G format required by config\_yield\_anchors. This means 11 of 12 staff cannot be yield-benchmarked. This is a significant data integrity issue that affects yield calculations for the majority of the team. No owner is named and no resolution date is given.

**VALIDATOR-GAP-004 · config\_metric\_values covers only 22% of tasks — no escalation path** Nine metrics are missing from the registry. GBB typo affects five entries. The duplicate ROAS entry must be removed. These three issues together mean that yield calculations are incomplete for 78% of all tasks. This is not a minor configuration issue — it means the dashboard is showing partial data as if it were complete data. This must be escalated with a named owner.

**VALIDATOR-GAP-005 · No recovery procedures documented for any failure** The Three-Am Standard requires that a developer can recover from failures using only the skill file. There are no recovery steps anywhere in this file. What happens if the Step 0 query fails? What happens if the dashboard artifact breaks? What happens if a LEFT JOIN ph\_master starts dropping rows after a schema change? None of these scenarios are addressed.

**VALIDATOR-GAP-006 · config\_departments has zero matching rows — no fix path documented** Section 8 correctly warns "Never JOIN config\_departments — zero rows match." But there is no explanation of why it has zero matches, whether this is expected or a data error, and whether it should ever be fixed. A developer reading this in the future does not know if config\_departments is intentionally empty or broken.

**VALIDATOR-GAP-007 · TECH department mapping decision is unresolved** Section 7 asks "Decide on TECH department mapping — is it separate from Technical / GTM and UI-UX?" This is an open question with no owner and no deadline. Until it is resolved, queries that group departments may produce inconsistent results depending on whether TECH is treated as a separate department or merged with the Technical categories.

---

### **PART 5 — EXTRACTED BUSINESS LOGIC AND SKILLS (PLAIN LANGUAGE)**

**Logic 1 — What the EOD System Tracks** The EOD performance system is a daily task logging system for 12 staff across 5 departments. Every task logged has a staff member, department, tier (S/A/B/C/D), metric type, delta score, hours spent, and a verified flag. The system is used by management and HR to track how many hours are being spent on high-value work, who is verifying their claims, and where time is being wasted. The data lives in a PostgreSQL database called the ROI database at vintageinterior.co.uk, in a table called daily\_eod\_log.

**Logic 2 — The Live Step 0 Query Must Run Before Every Session** The skill file used to have fixed numbers baked in — like "865 tasks" and "data ends April 3." Every time new CSV data was uploaded, these numbers became wrong and queries would give incorrect answers. The fix was to replace all hardcoded numbers with a live SQL query called Step 0, which runs at the start of every session and fetches the current row count, date range, staff count, verified count, and waste count directly from the database. Any developer or LLM using this system must run Step 0 first. Skipping it means working with stale numbers.

**Logic 3 — Always Use LEFT JOIN for ph\_master, Never INNER JOIN** The staff master table ph\_master does not have a record for every staff member who has logged tasks. Currently DMT001 (Piranav) has 60 task records in daily\_eod\_log but no matching record in ph\_master. If a query uses INNER JOIN ph\_master, it will silently drop Piranav's 60 records from all results. Always use LEFT JOIN ph\_master to keep all staff in the output regardless of whether they have a master record or not.

**Logic 4 — verified and waste\_flag Are Numbers, Not True/False** The verified and waste\_flag columns store the number 1 for true and 0 for false. They are not boolean columns. Any query that checks `verified = TRUE` or `waste_flag = TRUE` will fail to find matching rows and will return incorrect results. The correct syntax is `verified = 1` and `waste_flag = 1`. This is a silent failure — the query will run without error but produce wrong answers.

**Logic 5 — Always TRIM the Department Column** The department column in daily\_eod\_log has trailing spaces in the stored values. If a query groups by department without trimming the spaces, it will create separate groups for "Google Ads" and "Google Ads " and split the results incorrectly. Always write `TRIM(l.department)` in any GROUP BY clause that includes department.

**Logic 6 — Always Filter config\_metric\_values by Currency GBP** The config\_metric\_values table has two entries for the ROAS metric — one in GBP and one in another currency. If a query joins config\_metric\_values without filtering by currency, ROAS rows will be duplicated and calculations will be wrong. Always add `AND mv.currency = 'GBP'` to any join on config\_metric\_values.

**Logic 7 — Never Join config\_departments** The config\_departments table exists in the database but has zero rows that match the department values in daily\_eod\_log. Any query that tries to join config\_departments to daily\_eod\_log will return zero results or silently drop all rows. Do not use config\_departments in any join until the data mismatch is resolved.

**Logic 8 — The Date Column Is a Timestamp, Not a Date** The date column in daily\_eod\_log stores a full timestamp including time. Any query that compares it to a plain date will behave unexpectedly. Always cast the column using `::date` when doing date comparisons, for example `l.date::date = '2026-04-24'`.

**Logic 9 — TECH Is a Separate Department and Does Not Merge With Technical / GTM or Technical / UI-UX** The database has three department values that sound similar: TECH, Technical / GTM, and Technical / UI-UX. TRIM does not merge these — they are stored as three distinct values. Any query that tries to group all technical departments together must handle them as three separate entries. Assuming TECH is the same as Technical / GTM will produce incorrect department summaries.

**Logic 10 — Yield Calculations Are Only 22% Complete** The config\_metric\_values registry only covers about 22% of all tasks logged. Nine metric types have no GBP base value recorded. This means that for 78% of tasks, a true monetised yield cannot be calculated. Delta per hour figures are available for all rows but these are not monetised. Any yield report produced from this system is a partial picture, not a complete one. Until the registry is expanded to cover all metric types, yield totals will understate true performance.

**Logic 11 — SEO Staff Have the Highest Delta Scores and the Lowest Verification** SEO department staff claim delta per hour values between 9 and 15, which are the highest in the company. At the same time, SEO has a 4.3% verification rate — four staff have never submitted a verification URL. This creates a data quality risk: the highest-performing numbers in the system are the least verified. Management should not rely on SEO delta scores for decisions until verification URLs are submitted.

**Logic 12 — The Dashboard Will Return Zero Rows for All Time-Windowed Questions Until New Data Is Uploaded** Questions that ask about this week, this month, or the last 28 days are built on time-windowed SQL queries. The most recent data in the system is from April 24 2026\. As of June 3 2026, that is a 40-day gap. Every time-windowed question will return zero rows until May and June 2026 CSV data is uploaded. This is not a system bug — it is a data gap.

---

### **PART 6 — VALIDATION RULES**

Section 5 is absent from this file under the correct mandatory name. The following rules were extracted from Section 8 and Section 2 and are presented here as they should appear in a properly structured Section 5 on resubmission.

**Rule 1 — Bigint Comparison Rule** The verified and waste\_flag columns must always be compared using `= 1` not `= TRUE`. These columns are bigint type, not boolean. Queries using boolean comparison will silently return zero rows. Every query that filters on verified tasks or waste tasks must use this pattern.

**Rule 2 — Department TRIM Rule** The department column must always be wrapped in `TRIM(l.department)` in any GROUP BY or WHERE clause. Raw department values contain trailing spaces. Queries without TRIM will split department groups incorrectly and produce wrong aggregation results.

**Rule 3 — LEFT JOIN ph\_master Rule** All queries must use LEFT JOIN when joining ph\_master to daily\_eod\_log. INNER JOIN will silently drop staff members who have no ph\_master record. Currently DMT001 (Piranav) with 60 rows has no ph\_master record and would be dropped by any INNER JOIN.

**Rule 4 — GBP Currency Filter Rule** All joins on config\_metric\_values must include `AND mv.currency = 'GBP'`. The ROAS metric has two entries with different currencies. Without the currency filter, ROAS calculations will be duplicated.

**Rule 5 — Date Cast Rule** The date column in daily\_eod\_log is a timestamp. Date comparisons must always cast the column: `l.date::date`. Plain date comparisons against a timestamp column will behave unpredictably.

**Rule 6 — config\_departments Exclusion Rule** Never JOIN config\_departments to daily\_eod\_log. Zero rows in config\_departments match the department values in daily\_eod\_log. Any join using this table will return zero results or silently remove all rows.

**Rule 7 — Step 0 Must Execute First** Before answering any question about the EOD system, the Step 0 live query must execute to fetch current counts from the database. Skipping Step 0 and relying on cached or hardcoded numbers will produce incorrect answers whenever new CSV data has been uploaded since the last session.

---

### **PART 7 — SUMMARY OF ALL GAPS**

**Gaps registered by the developer (from Sections 5 and 7):**

GAP-D-01: May and June 2026 EOD data not uploaded. 40-day data gap. All time-windowed questions return 0 rows. Owner: not assigned. Blocking: YES for time-windowed queries.

GAP-D-02: SEO department verification failure. Hetheesha (0%), Kamsi (0%), Sukirtha (0%), Dilaksi (17.1%) have not submitted verification URLs. Owner: not assigned. Blocking: PARTIAL — data exists but cannot be confirmed.

GAP-D-03: ph\_master.band not standardised to A–G format. 11 of 12 staff cannot be yield-benchmarked. Owner: not assigned. Blocking: YES for yield calculations.

GAP-D-04: DMT001 (Piranav) missing from ph\_master. 60 rows unlinked. Owner: not assigned. Blocking: PARTIAL — data is included via LEFT JOIN but not enriched with master data.

GAP-D-05: config\_metric\_values covers only 22% of tasks. 9 metrics missing. GBB typo on 5 entries. Duplicate ROAS entry. Owner: not assigned. Blocking: YES for complete yield calculations.

GAP-D-06: config\_departments.department\_id does not align to daily\_eod\_log department values. Owner: not assigned. Blocking: NO — the rule is to never join this table.

GAP-D-07: TECH department mapping unresolved — is it separate from Technical / GTM and UI-UX? Owner: not assigned. Blocking: PARTIAL — department grouping queries are ambiguous.

**Additional gaps identified by validator:**

VALIDATOR-GAP-001: All 7 developer gaps above have no owner assigned and no resolution deadline. Without owners, none of these gaps will close.

VALIDATOR-GAP-002: No recovery procedures documented for any failure scenario. Step 0 query failure, dashboard artifact breakage, and ph\_master schema changes all have no documented recovery path.

VALIDATOR-GAP-003: config\_departments zero-match situation has no explanation of whether it is intentionally empty or a data error, and no path to resolution.

VALIDATOR-GAP-004: The five changes in Section 2 have no Git commit evidence. None of the five changes can be traced to a specific implementation artifact.

VALIDATOR-GAP-005: Section 9 self-assessment incorrectly states metadata is complete. Two mandatory fields are missing. The self-check failed to catch its own metadata gap.

---

### **PART 8 — FINAL VERDICT**

**Score: 60 / 100 — Requires Revision**

This file has genuinely strong content. Section 8 is one of the best company knowledge extracts seen in files reviewed so far. The structural rules are precise, implementable, and carry real operational value — the bigint rule, the TRIM rule, the LEFT JOIN rule, and the GBP currency filter are exactly the kind of silent failure traps that save future developers hours of debugging. The plain-language explanations in Section 2 are a standout quality — every change is followed by a sentence explaining what it means in business terms. This is good practice and should be continued.

However three categories of issues are preventing this file from scoring higher.

The first category is structural. Five of nine section names are wrong. This is not a cosmetic issue — it directly breaks the LLM compilation pipeline's ability to retrieve content from this file by section. The fix takes less than five minutes: rename the five headings to their mandatory names. The content inside largely does not need to change.

The second category is BLOS governance. Both blos\_keys\_used and hardcoded\_thresholds are absent from the metadata. These are mandatory fields and their absence is a rejection condition under Rule 5\.

The third category is gap discipline. Seven operational gaps are identified in the file but none of them have an owner and none have a blocking status. A gap without an owner is a gap that will never be resolved. Every gap entry must name a person responsible and state whether it is blocking progress.

**Required corrections before resubmission:**

First, rename Sections 3 through 7 to their mandatory v3.0 names.

Second, add blos\_keys\_used and hardcoded\_thresholds to the metadata block. If no BLOS keys were used, state NONE. If no thresholds are hardcoded, state NONE.

Third, move the six reporting fields (data\_range, total\_tasks\_logged, etc.) out of the metadata block and into Section 1 content.

Fourth, create a proper GAP FOUND section (Section 4\) with all seven gaps listed in the correct format — what is missing, blocking status, and owner for each.

Fifth, create a proper VALIDATION RULE ADDED OR CHANGED section (Section 5\) using the seven rules extracted in Part 6 of this report.

Sixth, create a DECISIONS MADE TODAY section (Section 7\) documenting at minimum the decision to replace hardcoded values with the live Step 0 query — including why this was chosen and what risk it creates.

Seventh, add Git commit hashes or file paths for the five changes documented in Section 2\.

Once these corrections are made, this file has the content quality to score in the 82 to 87 range.

---

*End of validation report. DIGITWEB LK LTD. — Skill File Validator — v3.0 — 2026-06-03*

