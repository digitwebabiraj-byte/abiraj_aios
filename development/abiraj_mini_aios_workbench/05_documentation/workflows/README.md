# workflows (nested under 05_documentation)

## Purpose

Holds workflow exports and workflow documentation. Maps the Technical Setup Guide's 'Workflow exports and workflow documentation' output type into the numbered architecture.

## Accepted Assets

- Exported workflow definitions (e.g. n8n / OpenFlow JSON) as documentation
- Written explanations of how a workflow operates
- Diagrams and notes describing workflow behaviour

## Not Allowed

- Live execution of n8n or OpenFlow workflows
- Secrets, tokens or credentials embedded in exports
- Proof-of-work evidence (belongs in 06_evidence)

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
