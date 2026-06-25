### **SKILL FILE VALIDATION REPORT**

**File:** 2026-06-08\_\_abiraj\_\_eod\_\_REQ-03-D03.md **Developer:** Abiraj **Project:** EOD Performance Tracker (eod) **Validated on:** 2026-06-09 **Validator:** Claude (DIGITWEB LK LTD. Skill File Validator) **Overall Score: 78 / 100 — Accepted with Corrections Required**

---

#### **PART 1 — FORMAT AND TEMPLATE COMPLIANCE**

**File Naming Standard — Pass** The filename correctly uses YYYY-MM-DD format (2026-06-08). Double underscores separate all segments. Developer name is lowercase. Project code is eod. Deliverable ID is REQ-03-D03. The submission checklist confirms this canonical name and it matches the actual uploaded file. This is the first EOD file from Abiraj with a fully compliant filename across all segments. Full marks here.

**REQ-ID and Deliverable-ID Sequence — Pass** The file declares REQ-03-D03 which correctly continues from REQ-03-D01 and REQ-03-D02. The REQ-ID is consistent and the deliverable ID increments correctly. This sequencing was violated in D01 and corrected in D02 — it is maintained correctly here.

**Section Structure — Partial Pass** The file contains nine numbered sections. Sections 1, 2, 8, and 9 are correctly labelled with mandatory v3.0 names. The same five section label violations from D01 and D02 persist unchanged in D03:

Section 3 is labelled TODAY'S ACTIVITY LOG instead of the mandatory POSTGRESQL / MCP / DATABASE FINDING. Section 4 is labelled CUMULATIVE PERFORMANCE SUMMARY instead of the mandatory GAP FOUND. Section 5 is labelled ISSUES & ALERTS instead of the mandatory VALIDATION RULE ADDED OR CHANGED. Section 6 is labelled WASTE LOG instead of the mandatory FAILURE MODE OR EDGE CASE. Section 7 is labelled OPEN ITEMS instead of the mandatory DECISIONS MADE TODAY.

This is the third consecutive EOD file from this developer with the same five section label violations uncorrected. The D01 and D02 validation reports both listed these as required corrections. They have not been applied in D03. Under the validator escalation policy stated during this session, three consecutive uncorrected violations on the same fields will result in a formal metadata block or structure rejection on the next submission. D04 will be formally rejected on section structure if these five labels are not corrected.

The content under each section is relevant and well-organised for its purpose — the issue is purely the labels, which affect LLM compilation pipeline indexing.

**Metadata Block — Partial Pass** Significant improvement over D01 and D02 is noted. The three\_am\_standard correctly declares PASS rather than the incorrect TRUE used in both prior files. llm\_queryable and company\_knowledge\_candidate correctly declare YES. All 15 required fields are present. The metadata uses a markdown table format which is non-canonical but consistent with this developer's pattern.

Three issues remain. First, six non-standard reporting fields are still present in the metadata block: data\_range, total\_tasks\_logged, total\_hours\_logged, verification\_rate, high\_value\_pct, and waste\_hours. These were flagged in D01 and D02 as belonging in Section 1 or Section 4 content, not in the metadata governance block. They remain for the third consecutive file. Second, blos\_keys\_used is absent from the metadata — this mandatory field must declare NONE if no BLOS keys were used. Third, hardcoded\_thresholds is absent — this mandatory field must be present. The 39/6/3 question capability split and the time-window fallback behaviour could be interpreted as governed rules. Even if no thresholds exist, the field must declare NONE.

**Evidence Location — Pass** The evidence\_location field references daily\_eod\_log — PostgreSQL · ROI database · vintageinterior.co.uk. Every data claim in the file is sourced from this live database. Section 8 confirms the MCP endpoint at eod-mcp.vintageinterior.co.uk/sse. The Step 0 live query pattern means all numbers are pulled at query time from the live database — this is strong evidence practice. Rule 7 is satisfied.

**BLOS Governance — Partial Pass** Both blos\_keys\_used and hardcoded\_thresholds are absent from the metadata. This was flagged in D01 and D02. The Section 8 company knowledge extract identifies two data-integrity rules (ph\_id uniqueness check and department canonicalisation) that function as validation rules requiring BLOS-level governance. These are documented correctly in Section 8 but neither field is present in the metadata governance block. This is a third consecutive violation on both fields.

**Three-Am Standard — Pass** The developer correctly self-declares PASS and the Section 9 self-assessment is the most thorough and specific of any EOD file reviewed. It covers WHAT was done, WHAT changed in the data, WHAT is newly broken, WHO needs action, WHY the skill held up, WHERE everything lives, and WHAT to do next. A developer at 3AM would have complete operational context from this section alone. This is a genuine improvement from D02.

**Credentials in File — Pass** No passwords, API keys, tokens, or database credentials are present. The MCP server URL and database host are referenced as operational endpoints but are not security-sensitive in this internal knowledge context.

**Submission Checklist — Pass** A full submission checklist is present. Four open items are correctly flagged as unresolved with warning symbols. This is good practice and demonstrates self-awareness of outstanding work. The checklist correctly marks the filename as compliant.

**Plain Language Summaries — Notable Strength** Every significant change in Section 2 is accompanied by an "In plain terms" paragraph. This continues the pattern from the Abiraj dlmt files and is not a v3.0 requirement but directly supports the company knowledge extraction objective. The plain language summaries for the ph\_id collision and ADS department fragmentation findings are particularly well-written and immediately usable by HR and management without technical interpretation.

---

#### **PART 2 — SCORING**

| Area | Score | Out of |
| ----- | ----- | ----- |
| Metadata Completeness | 6 | 10 |
| Structure Compliance | 5 | 10 |
| Business Logic Clarity | 18 | 20 |
| Validation Rule Quality | 5 | 15 |
| Gap Identification | 9 | 10 |
| Edge Case Documentation | 8 | 10 |
| Evidence Referencing | 9 | 10 |
| LLM Queryability | 18 | 15 |
| **Total** | **78** | **100** |

Metadata loses four marks for the absent blos\_keys\_used field, the absent hardcoded\_thresholds field, and the six non-standard reporting fields still in the metadata block — all three are repeat violations from D01 and D02. Structure loses five marks for the same five mislabelled sections as D01 and D02 — a third consecutive uncorrected violation. Business logic clarity loses two marks because the ph\_id collision and ADS department fragmentation findings are well documented but the business impact on HR reporting accuracy is described only qualitatively — no estimate of how many queries or reports are currently producing wrong results due to these issues. Validation rule quality loses ten marks — Section 5 (ISSUES & ALERTS) contains no validation rules with rule IDs, conditions, or prevention logic. The two data-integrity rules identified in Section 8 should be in Section 5\. Gap identification loses one mark because the open items in Section 7 have no named owners — all eleven items are ownerless. Edge case documentation loses two marks because Section 6 (WASTE LOG) documents waste categories but does not follow the failure mode structure (trigger, detection, recovery, risk level) required by the mandatory section. Evidence gains above the ceiling note because the Step 0 live query pattern and the MCP-sourced real-time data are exemplary evidence practice — every number in the file is live-database-sourced with no hardcoded values. LLM queryability scores high for the same reason — the verification trend table, staff performance table, department summary, and tier distribution are all directly LLM-queryable reference data.

---

#### **PART 3 — GAPS FOUND — FORMAT AND CONTEXT**

**FORMAT-GAP-01 · Five mandatory section labels still wrong — third consecutive file** The D01 and D02 validation reports both explicitly listed all five wrong section names as required corrections. All five appear unchanged in D03 with the same custom labels. The submission checklist marks sections as complete — this self-check did not catch the labelling violations. This is now a confirmed third consecutive repeat violation. Under the validator escalation policy, D04 will be formally rejected on section structure if these five labels are not corrected before submission.

Section 3 must be labelled: POSTGRESQL / MCP / DATABASE FINDING Section 4 must be labelled: GAP FOUND Section 5 must be labelled: VALIDATION RULE ADDED OR CHANGED Section 6 must be labelled: FAILURE MODE OR EDGE CASE Section 7 must be labelled: DECISIONS MADE TODAY

**FORMAT-GAP-02 · blos\_keys\_used absent — third consecutive file** The mandatory blos\_keys\_used metadata field is not present. Must declare NONE if no BLOS keys were used. This was flagged in D01 and D02.

**FORMAT-GAP-03 · hardcoded\_thresholds absent — third consecutive file** The mandatory hardcoded\_thresholds metadata field is not present. Must declare NONE if no thresholds exist or list any operational values that are fixed in the skill or query system. This was flagged in D01 and D02.

**FORMAT-GAP-04 · Six non-standard fields still in metadata block — third consecutive file** data\_range, total\_tasks\_logged, total\_hours\_logged, verification\_rate, high\_value\_pct, and waste\_hours are reporting numbers that belong in Section 1 or Section 4 content, not in the governance metadata block. This was flagged in D01 and D02 and remains unchanged.

**FORMAT-GAP-05 · Section 5 (ISSUES & ALERTS) contains no validation rules** Section 5 in v3.0 is VALIDATION RULE ADDED OR CHANGED. The current content documents issues and alerts — which is valuable but belongs in the GAP FOUND section. Two new data-integrity rules were identified today (ph\_id uniqueness check and department canonicalisation pre-insert validation) and are correctly documented in Section 8\. These must also appear in Section 5 as formally numbered validation rules with conditions, prevention logic, and implementation references.

**FORMAT-GAP-06 · Section 6 (WASTE LOG) does not follow failure mode structure** Section 6 in v3.0 is FAILURE MODE OR EDGE CASE. The current content is a waste log table. The waste entries describe what went wrong but do not follow the mandatory failure mode structure: trigger condition, detection method, recovery procedure, and risk level. The waste log data is valuable and should be incorporated into properly structured failure mode entries, or presented as supporting data within a Section 6 that follows the required format.

**FORMAT-GAP-07 · Section 7 (OPEN ITEMS) does not document decisions** Section 7 in v3.0 is DECISIONS MADE TODAY. The current content is a list of open action items. At minimum two decisions were made today: the decision to surface the ph\_id collision and ADS department fragmentation as critical findings rather than warnings, and the decision to recommend pre-insert validations for the upload skill. These must appear in Section 7 with alternatives considered and reasons for choice. The open items list belongs in Section 4 (GAP FOUND).

**FORMAT-GAP-08 · All eleven open items have no named owner** Every item in Section 7 is ownerless. The ph\_id collision (CRITICAL), ADS department merge (CRITICAL), Sukirtha 0% verification (CRITICAL), June upload (CRITICAL), and all seven OPEN items have no named individual assigned. Without named owners these items have no accountability mechanism and will not close.

**CONTENT-GAP-01 · ph\_id collision DMK004 — impact on current reports not quantified** The collision between Thasitha and Thisoban on DMK004 is correctly identified and flagged as CRITICAL. However the current impact on existing reports is not stated. How many current query results show incorrect per-staff data due to this collision? How many rows in daily\_eod\_log are affected? Without quantifying the impact, management cannot prioritise the correction relative to other work. No owner assigned for the re-coding task.

**CONTENT-GAP-02 · ADS department merge — no resolution owner or target date** The ADS code covering 205 tasks and 398.5 hours of work for what appears to be the same Google Ads team is correctly flagged as CRITICAL. However the decision about which canonical department code to use (merge ADS into Google Ads, or rename Google Ads to ADS, or create a new unified code) has not been made. No owner is named for this decision. No target date is set.

**CONTENT-GAP-03 · Five unmatched ph\_ids — no master data creation owner or timeline** Three new starters (Theekshy DMK005, Thanishtika DMK006, Jakshan DMKS05) plus two carried from D02 (Piranav DMT001, Dilaksi PH061) are missing from ph\_master. Band, yield, and limit data is NULL for all five. No owner is assigned for adding these records. No target date.

**CONTENT-GAP-04 · config\_metric\_values gaps carried from D02 — no resolution progress** The gap covering 9 missing metrics, the GBB typo on 5 entries, and the duplicate ROAS row was registered in D02 and carried forward unchanged with no progress, no owner, and no target date. This is the third file in which this gap appears unresolved.

---

#### **PART 4 — GAPS DOCUMENTED IN THE FILE**

These are the items the developer registered in Section 5 (Issues and Alerts) and Section 7 (Open Items).

**Critical — Data Integrity (NEW)**

Gap 1 — ph\_id collision DMK004: Thasitha and Thisoban share one ph\_id. Any per-staff query keyed on ph\_id will merge or misattribute their work. Resolution required: re-code one person to a unique ph\_id. No owner. No due date.

Gap 2 — ADS department code duplicating Google Ads: 205 tasks and 398.5 hours belonging to Google Ads staff are logged under a second code ADS. Department-level totals are split across two labels for one team. Resolution required: decide canonical code and remap. No owner. No due date.

**Critical — Verification**

Gap 3 — Sukirtha 0% verification: 116 tasks, 169.5 hours, zero proof URLs. Unchanged since D02. No owner. No due date.

Gap 4 — Dilaksi at 17.1%: High claimed metric delta per hour (15.64) remains largely unconfirmed. No owner. No due date.

**Warning — Master Data Gaps**

Gap 5 — Five ph\_ids unmatched in ph\_master: Theekshy (DMK005), Thanishtika (DMK006), Jakshan (DMKS05), Piranav (DMT001), Dilaksi (PH061). Band/yield/limit data is NULL. No owner. No due date.

**Warning — Registry Gaps (carried from D02)**

Gap 6 — ph\_master.band not standardised to A–G. Carries from D01 and D02.

Gap 7 — config\_metric\_values covers only approximately 22% of tasks. 9 metrics missing, GBB typo, duplicate ROAS row. Carries from D01 and D02.

**Open Items (from Section 7\)**

Eight additional open items are registered: upload June 2026 EOD CSV, add three new starters to ph\_master, standardise ph\_master.band, fix config\_metric\_values, fix GBB typo, remove duplicate ROAS entry, and rebuild dashboard artifact. None have owners or due dates.

---

#### **PART 5 — ADDITIONAL GAPS IDENTIFIED BY VALIDATOR**

**VALIDATOR-GAP-001 · Three repeat violations confirmed — D01 and D02 feedback not fully applied** FORMAT-GAP-01 (section names), FORMAT-GAP-02 (blos\_keys\_used), FORMAT-GAP-03 (hardcoded\_thresholds), and FORMAT-GAP-04 (non-standard metadata fields) were all explicitly flagged in both D01 and D02 validation reports as required corrections. All four appear unchanged in D03. The submission checklist marks metadata as complete, confirming the feedback was not applied before D03 was submitted. D04 will receive a formal section structure rejection if the five section labels are not corrected.

**VALIDATOR-GAP-002 · Two newly identified data-integrity rules not captured in Section 5** Section 8 documents two important pre-insert validation rules that should be added to the upload skill: a ph\_id uniqueness check (verify each ph\_id maps to exactly one ph\_name before insert) and a department canonicalisation warning (flag near-synonym department codes before creating parallel entries). These are formal business rules with conditions, prevention logic, and implementation targets. They must appear in Section 5 as numbered rules with rule IDs on the next resubmission.

**VALIDATOR-GAP-003 · Sajeepan is listed in both Google Ads and CRITICAL open items without explanation** The staff table shows Sajeepan assigned to Google Ads department. Section 5 identifies ADS as duplicating Google Ads staff and lists Sajeepan among the ADS members. This creates an ambiguity — is Sajeepan in Google Ads, ADS, or both? The department fragmentation may mean Sajeepan is being counted in both department totals simultaneously. The file does not confirm whether any staff members appear in both department counts.

**VALIDATOR-GAP-004 · Jakshan ph\_id is DMKS05 — possible typo suggesting it should be DMK05** The new starter Jakshan is logged with ph\_id DMKS05. All other DMK series IDs use the pattern DMK00N (DMK001, DMK002, etc.) or DMKNNN (DMK004, DMK005, DMK006). DMKS05 has an S inserted that no other ID has. This may be a data entry typo. If Jakshan's correct ID is DMK005 or another standard format, the S variant will never match query filters using the clean pattern. This should be verified before the ph\_master record is created for this person.

**VALIDATOR-GAP-005 · Dilaksi Δ/hr of 15.64 with 17.1% verification is a data quality risk not escalated** The staff table shows Dilaksi with the third-highest metric delta per hour (15.64) across 82 tasks and 134 hours, but only 17.1% of those tasks have proof URLs. Section 5 notes this as a warning but does not escalate it. A staff member claiming high value output with 83% of tasks unverified represents a data integrity risk equivalent to Sukirtha's 0%. The file should explicitly flag Dilaksi as CRITICAL alongside Sukirtha, not as a lower-priority warning.

**VALIDATOR-GAP-006 · Dashboard artifact rebuild listed as OPEN with no owner or target date** Section 7 lists rebuilding the dashboard artifact against the new 1,782-row dataset as an open item. The D02 report documented the FastAPI standalone dashboard as the HR-facing system. If the dashboard is still showing D02 data (1,006 rows, April endpoint), HR is working from stale figures. This is an operational risk that should have a named owner and an urgent due date.

**VALIDATOR-GAP-007 · MCP server URL documented but no failure handling or restart procedure** Section 9 and Section 8 reference eod-mcp.vintageinterior.co.uk/sse as the MCP endpoint. This was first documented in D02. The failure handling, authentication method, restart procedure, and ownership for this MCP server remain undocumented across both D02 and D03. Since the entire query skill depends on this connection, its operational procedures should be formally captured.

---

#### **PART 6 — EXTRACTED BUSINESS LOGIC AND SKILLS (PLAIN LANGUAGE)**

**Logic 1 — The Step 0 Live Query Pattern Protects Against Stale Reports** Every number in this EOD report was fetched live from the PostgreSQL database at query time, not hardcoded. This means the skill file does not need to be manually updated every time new data is uploaded. The Step 0 query at the start of every session fetches current row count, date range, staff count, verified count, and waste count directly from daily\_eod\_log. Any report generated from this skill will always reflect the most current data in the database, not the figures from the last time the skill file was edited. The verification trend table in Section 8 shows how this approach works in practice — the D02 figures (53.2% overall, 4.3% SEO) and the D03 figures (73.6% overall, 48.5% SEO) are different because they reflect different data states, not because the skill was rewritten.

**Logic 2 — A ph\_id Must Uniquely Identify One Person Across All Time** The ph\_id is the primary key for staff identity in the EOD system. Every query that ranks staff performance, calculates yield, assigns band limits, or builds a career history depends on ph\_id identifying exactly one person. When two people share the same ph\_id (as Thasitha and Thisoban both share DMK004), any per-staff query merges their work into a single result. A report showing DMK004 with 38 hours at 100% verification may be showing data from both people combined, or only from whichever person the database returned first. Until one of them is re-coded to a unique ID, all per-staff analytics for either person are unreliable.

**Logic 3 — TRIM Merges Whitespace But Cannot Merge Synonym Department Codes** The EOD query system uses TRIM(l.department) to normalise whitespace variations in department names — for example TRIM merges Google\_Ads and Google\_Ads (space at end) into a single label. However TRIM cannot merge two genuinely different strings that mean the same thing. ADS and Google Ads are different strings and will always appear as separate departments in any GROUP BY department query. The only way to merge them is a data decision: choose one canonical code, run an UPDATE to remap all rows using the non-canonical code, and enforce the canonical code on future CSV uploads. This must happen before any department-level reporting is considered accurate.

**Logic 4 — LEFT JOIN ph\_master Is Mandatory — INNER JOIN Silently Drops Staff** All queries that enrich staff data with band, yield anchor, or limit information must join daily\_eod\_log to ph\_master using a LEFT JOIN, never an INNER JOIN. As of D03, five ph\_ids in daily\_eod\_log have no corresponding row in ph\_master (Theekshy, Thanishtika, Jakshan, Piranav, Dilaksi). An INNER JOIN would silently exclude these five staff members from any result — their tasks and hours would disappear from totals and rankings without any error or warning. A LEFT JOIN keeps them visible with NULL values for band and yield columns, which is the correct behaviour because it shows the data gap rather than hiding it.

**Logic 5 — Time-Window Queries Must Detect Empty Results and Fall Back to All-Time** Three of the fifty predefined questions (Q1, Q9, Q15) use time windows: this week, this month, and last 28 days. When the current date falls outside the data range — as it does today with the last log dated 29 May and today being 8 June — these queries return zero rows. The skill file implements a fallback: when a time-window query returns zero rows, the system reports the actual data date range instead of returning an empty result or an error. This fallback must be preserved in any future version of the skill. The D03 test confirmed it works correctly against the larger 1,782-row dataset — zero rows for this week was correctly handled.

**Logic 6 — Two Pre-Insert Validations Must Be Added to the CSV Upload Skill** The D03 data integrity findings argue for adding two checks to the tally.md upload skill before any new CSV is inserted into daily\_eod\_log. First, a ph\_id uniqueness check: before inserting rows from a new CSV, verify that each ph\_id in the incoming data maps to only one distinct ph\_name across both the existing table and the new file. Flag any ph\_id that appears with more than one name as a collision requiring manual review before the insert proceeds. Second, a department canonicalisation warning: compare all department strings in the new CSV against existing canonical department codes and warn when a new string is a close synonym of an existing one rather than creating a new parallel code silently. Both rules prevent data integrity errors from entering the system rather than detecting them after the fact.

**Logic 7 — High Δ/hr With Low Verification Is a Data Quality Risk, Not a Performance Signal** The metric delta per hour (Δ/hr) is a productivity indicator calculated as metric\_delta divided by hours logged. A high Δ/hr value appears positive. However when the verification rate for that staff member is low, the metric\_delta values themselves are unconfirmed — they are self-reported without proof URLs. The three SEO staff with the highest Δ/hr (Kamsi 20.03, Hetheesha 16.62, Dilaksi 15.64) all have verification rates below 45%. This means their high productivity figures are largely unverified claims. High Δ/hr should only be treated as a confirmed performance signal when verification is above an acceptable threshold. Below that threshold it should be treated as a data quality risk and flagged as such in HR reports.

**Logic 8 — The Verification Trend Is Auditable Across Deliverables** Section 8 contains a verification trend table showing the D02 and D03 states side by side (1,006 rows at 53.2% overall vs 1,782 rows at 73.6% overall). This cross-deliverable tracking is a deliberate design — each skill file contributes a snapshot to a growing historical record that management can audit over time. The verification improvement from 4.3% to 48.5% in SEO specifically can be attributed to the May data upload and is evidence that the 0% alert in D02 prompted corrective action from most SEO staff (Hetheesha 0% → 44.2%, Kamsi 0% → 80%). Sukirtha remains the exception.

---

#### **PART 7 — VALIDATION RULES DOCUMENTED IN THE FILE**

Section 5 is labelled ISSUES & ALERTS and contains no formal validation rules. The following rules were identified in Section 8 (Company Knowledge Extract) and are presented here as they must appear in a properly structured Section 5 on resubmission.

**Extracted Rule 1 — ph\_id Uniqueness Pre-Insert Validation** Condition: Before inserting any CSV row into daily\_eod\_log, verify that each ph\_id in the incoming file maps to exactly one distinct ph\_name across both the existing table and the incoming data. If a ph\_id maps to two or more distinct names, the insert must be blocked and the collision flagged for manual review. Prevents: Data where two people share one identifier, making per-staff analytics unreliable. Implementation target: tally.md (eod-csv-upload skill). BLOS reference: None — should be registered as a governance rule.

**Extracted Rule 2 — Department Canonicalisation Pre-Insert Warning** Condition: Before inserting any CSV row into daily\_eod\_log, compare all department string values in the incoming data against the canonical department codes already in the table. If any incoming department string is a near-synonym of an existing code (for example ADS when Google Ads already exists), generate a warning to the operator before the insert proceeds rather than silently creating a parallel code. Prevents: Department fragmentation where one team's hours are split across multiple labels, breaking department-level totals. Implementation target: tally.md (eod-csv-upload skill). BLOS reference: None.

---

#### **PART 8 — SUMMARY OF ALL GAPS**

**Gaps registered by the developer:**

Critical Gap 1: ph\_id collision DMK004 — Thasitha and Thisoban share one ID. All per-staff queries for both are unreliable until resolved. No owner. No due date.

Critical Gap 2: ADS department code duplicating Google Ads — 205 tasks and 398.5 hours split across two labels for one team. No owner. No due date.

Critical Gap 3: Sukirtha 0% verification — 116 tasks, 169.5 hours, zero proof URLs. No owner. No due date.

Critical Gap 4: June 2026 EOD CSV not yet uploaded — 10-day data gap. No owner. No due date.

Open Gap 5: Three new starters (Theekshy, Thanishtika, Jakshan) missing from ph\_master. No owner. No due date.

Open Gap 6: Piranav and Dilaksi ph\_master records unconfirmed — carried from D02. No owner. No due date.

Open Gap 7: ph\_master.band not standardised to A–G. Carried from D01 and D02. No owner. No due date.

Open Gap 8: config\_metric\_values — 9 missing metrics, GBB typo on 5 entries, duplicate ROAS row. Carried from D01 and D02. No owner. No due date.

Open Gap 9: Dashboard artifact rebuild against 1,782-row dataset. No owner. No due date.

**Additional gaps identified by validator:**

VALIDATOR-GAP-001: Three repeat violations (section labels, blos\_keys\_used, hardcoded\_thresholds, non-standard metadata fields) from D01 and D02 not applied in D03. D04 section structure will be formally rejected if the five section labels are not corrected.

VALIDATOR-GAP-002: Two new data-integrity rules (ph\_id uniqueness check, department canonicalisation warning) must appear in Section 5 as formally numbered rules.

VALIDATOR-GAP-003: Sajeepan's department attribution is ambiguous — listed in Google Ads in staff table and in ADS member list in Section 5\. May be counted in both department totals simultaneously.

VALIDATOR-GAP-004: Jakshan ph\_id DMKS05 may be a typo — all other DMK IDs follow DMK00N pattern without the S character. Must be verified before ph\_master record is created.

VALIDATOR-GAP-005: Dilaksi Δ/hr of 15.64 with 17.1% verification is equivalent in risk to Sukirtha's 0% and should be escalated to CRITICAL rather than WARNING.

VALIDATOR-GAP-006: Dashboard artifact rebuild has no owner and no urgency classification despite HR currently working from stale D02 data.

VALIDATOR-GAP-007: MCP server at eod-mcp.vintageinterior.co.uk/sse has no documented failure handling, restart procedure, or ownership across D02 or D03.

---

#### **PART 9 — FINAL VERDICT**

Score: 78 / 100\. Accepted with corrections required.

D03 demonstrates meaningful progress in two areas. The metadata field value formats are now correct — three\_am\_standard is PASS, llm\_queryable is YES, company\_knowledge\_candidate is YES. The Three-Am Standard self-assessment in Section 9 is genuinely excellent — the most specific and actionable of any EOD file and strong enough to stand as a model for other developers. The plain language summaries are outstanding. The live-database-sourced figures, the verification trend table, and the two newly identified data-integrity rules in Section 8 are all high-quality company knowledge extraction.

However the score is held back by the same three categories as D01 and D02, now appearing for the third consecutive file without correction. The five wrong section labels have appeared across D01, D02, and D03 with zero change. The two missing mandatory metadata fields (blos\_keys\_used and hardcoded\_thresholds) have appeared in all three files. The six non-standard metadata fields have appeared in all three files. All three were listed as required corrections in both prior reports.

D04 formal rejection notice: If Section 3 is not labelled POSTGRESQL / MCP / DATABASE FINDING, Section 4 is not labelled GAP FOUND, Section 5 is not labelled VALIDATION RULE ADDED OR CHANGED, Section 6 is not labelled FAILURE MODE OR EDGE CASE, and Section 7 is not labelled DECISIONS MADE TODAY in D04, the section structure will be formally rejected and the file will not be accepted regardless of content quality.

Required corrections before D04 submission:

First, rename all five wrong section headings to their mandatory v3.0 names. This is a five-minute correction.

Second, add blos\_keys\_used: NONE and hardcoded\_thresholds: NONE to the metadata block.

Third, move the six reporting fields out of the metadata block into Section 1 content.

Fourth, move the open items list from Section 7 to Section 4, formatted with blocking status and named owner for each item.

Fifth, add a proper DECISIONS MADE TODAY section at Section 7 documenting the ph\_id collision escalation decision and the ADS/Google Ads canonical code decision.

Sixth, add a Section 5 containing the two data-integrity validation rules as formally numbered rules with conditions and prevention logic.

Seventh, assign a named owner to every critical open item — especially the ph\_id collision, the ADS merge, and Sukirtha's verification escalation.

Once these seven corrections are consistently applied from D04 onwards, the content quality in this file supports a score in the 88 to 92 range.

---

*End of validation report.* *DIGITWEB LK LTD. — Skill File Validator — v3.0 — 2026-06-09*

