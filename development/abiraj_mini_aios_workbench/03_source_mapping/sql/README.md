# sql (nested under 03_source_mapping)

## Purpose

Holds SQL used for inspection and DRAFT validation queries only. This is a read-and-draft location that maps the Technical Setup Guide's 'SQL inspection and draft validation queries' output type into the numbered architecture. It does not authorise running SQL against any live database.

## Accepted Assets

- SQL inspection scripts (read-only intent)
- Draft validation queries pending review
- Query drafts referenced by source maps in 03_source_mapping

## Not Allowed

- Executed migrations, schema drops or DDL changes
- Live credentials, secrets or connection strings
- Queries run against production without approval

## Source and Evidence Rule

Every important asset stored here must reference its source (where the truth came from) and its evidence (proof the work was done), with the evidence stored in `06_evidence` and linked by path. If an asset cannot point to a source and evidence, it is treated as not done and must not be relied upon.

## Owner and Reviewers

- Owner: Abiraj
- Coordinator: Varmen
- Technical Reviewer: Sajeesan
- Queryability Reviewer: Tamil Selvan
- Business Validator: Assigned according to task type

## Status

ACTIVE STRUCTURE - NO VALIDATED ASSETS YET

## Pass / Fail Rule

PASS if content stored here matches the folder purpose, has evidence where required and does not create duplicate truth.

FAIL if the folder contains vague notes, unsupported claims, duplicate assets, unapproved business rules or work outside the assigned scope.
