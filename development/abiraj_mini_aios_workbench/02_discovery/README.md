# 02_discovery

## Purpose

Holds existing-asset searches and repository inspection performed BEFORE any asset is created, so that reuse is preferred over duplication and parallel truth is prevented.

## Accepted Assets

- Existing-asset search records
- Repository inspection reports
- Duplicate-risk reports (GREEN / AMBER / RED)
- Source discovery notes pointing to where truth already lives

## Not Allowed

- Newly invented assets that belong in their target folder
- Conclusions with no record of what was actually inspected
- Business rules or production changes

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
