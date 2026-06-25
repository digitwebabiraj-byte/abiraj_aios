# 03_source_mapping

## Purpose

Holds maps that connect requirements and assets to their real sources of truth, so every claim can be traced back to where it came from.

## Accepted Assets

- File maps and source-to-target maps
- System maps and data-flow maps
- Database object references (read-only references only)
- API mappings
- Evidence-source relationships

## Not Allowed

- Executable SQL or migrations
- Live credentials, secrets or connection strings
- Unsourced diagrams presented as fact

## Source and Evidence Rule

Every important asset stored here must reference its source (where the truth came from) and its evidence (proof the work was done), with the evidence stored in `06_evidence` and linked by path. If an asset cannot point to a source and evidence, it is treated as not done and must not be relied upon.

## Owner and Reviewers

Owner: Abiraj

Coordinator: Varmen

Queryability Reviewer: Tamil Selvan

Technical Reviewer: Sajeesan when technical review is required.

Business Validator: Assigned according to the task type.

## Status

ACTIVE STRUCTURE - NO VALIDATED ASSETS YET

## Pass / Fail Rule

PASS if content stored here matches the folder purpose, has evidence where required and does not create duplicate truth.

FAIL if the folder contains vague notes, unsupported claims, duplicate assets, unapproved business rules or work outside the assigned scope.
