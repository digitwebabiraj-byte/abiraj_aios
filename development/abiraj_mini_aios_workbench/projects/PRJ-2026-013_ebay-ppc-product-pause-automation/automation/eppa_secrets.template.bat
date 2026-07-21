@echo off
REM ==== EPPA credentials ??? copy this file to eppa_secrets.bat and fill in the two passwords ====
REM eppa_secrets.bat is git-ignored (see automation/.gitignore) so passwords are never committed.
REM
REM TWO databases, two different roles:
REM   ledsone  = the DATA source, read-only. Server "ukvm" in pgAdmin.
REM              Same connection PRJ-2026-011 (EBPD) and PRJ-2026-012 (ERA) use.
set "LED_PGHOST=207.148.78.148"
set "LED_PGPORT=5432"
set "LED_PGDATABASE=ledsone"
set "LED_PGUSER=dbhub_readonly"
set "LED_PGPASSWORD="

REM   order_management_copy = the PUBLISH target only (tech_team_outputs.ph_task).
REM              Written as temp_user. Never read as a data source by this job.
set "PGHOST=149.28.134.54"
set "PGPORT=5435"
set "PGDATABASE=order_management_copy"
set "PGUSER=temp_user"
set "PGPASSWORD="

REM If PGPASSWORD is left blank the weekly job still rebuilds the files, but SKIPS the ph_task
REM refresh and says so in the log ??? the portal row would then go stale silently. Fill it in.

