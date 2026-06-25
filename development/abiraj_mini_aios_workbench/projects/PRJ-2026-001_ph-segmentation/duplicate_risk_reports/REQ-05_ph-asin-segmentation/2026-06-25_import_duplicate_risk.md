# PH Segmentation Import Duplicate-Risk Report

## Scope

Confirm that importing the approved seven-asset PH Segmentation set creates no duplicate or
parallel truth inside the project, and that no existing asset was overwritten.

## Sources Checked

The PH Segmentation project folder (`projects/PRJ-2026-001_ph-segmentation`) was scanned for
existing files matching the approved import filenames and their SHA-256 values before copying.

## Checksum Search

Before import, the project contained only prior governance docs (structure-creation and
project-registration evidence/validation, plus README/CLAUDE/PROJECT_HOME/TASK_REGISTER).
None matched any of the seven source SHA-256 values, and none used the canonical import
filenames. No checksum collision existed.

## Existing Asset Comparison

| Imported Asset | Existing Asset | Checksum Match | Decision |
|---|---|---|---|
| Protocol .docx (`d8b7ff18…`) | none | No | COPY once |
| Final HTML (`25dd9103…`) | none | No | COPY once (canonical) |
| Day-1 summary (`f25c7d70…`) | none | No | COPY once |
| Day-2 summary (`b70b3a9a…`) | none | No | COPY once |
| Claude link (`89c7e131…`) | none | No | COPY once |
| SQL engine (`0ca4818c…`) | none | No | COPY once |
| Monthly prompt (`236f7a3e…`) | none | No | COPY once |

## Duplicate Decisions

* canonical final HTML imported **once**;
* **no second HTML copy** stored;
* SQL imported **once**;
* historical monthly prompt imported **once**;
* source summaries imported **once each**;
* Claude link imported **once**;
* originals **remain in intake** (unchanged);
* **no overwrite occurred** (all destinations were new).

## Parallel-Truth Assessment

Each asset now has exactly one canonical location inside the Task ID subfolders, recorded in
`SOURCE_MANIFEST.md`. The intake folder is the external source (not project truth) and is
left untouched. No competing copies exist inside the project. The `Downloads/` look-alikes
were out of scope and not imported.

## Result

GREEN

## Pass / Fail Rule

PASS if every approved asset has exactly one canonical project copy with a matching checksum,
no existing file was overwritten, and no parallel truth was created. FAIL otherwise.
