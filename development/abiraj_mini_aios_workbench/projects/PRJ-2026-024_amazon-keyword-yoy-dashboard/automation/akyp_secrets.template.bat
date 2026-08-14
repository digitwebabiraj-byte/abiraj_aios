@echo off
REM ==== AKYP credentials - copy this file to akyp_secrets.bat and fill in the two passwords ====
REM akyp_secrets.bat is git-ignored. GLOBAL user env vars take precedence if already set.
REM   ledsone = DATA source, read-only (live host after the 2026-07-29 migration).
set "LED_PGHOST=169.58.91.229"
set "LED_PGPORT=5432"
set "LED_PGDATABASE=ledsone"
set "LED_PGUSER=dev_user"
set "LED_PGPASSWORD="
REM   order_management_copy = PUBLISH target only (tech_team_outputs.ph_task), written as temp_user.
set "PGHOST=149.28.134.54"
set "PGPORT=5435"
set "PGDATABASE=order_management_copy"
set "PGUSER=temp_user"
set "PGPASSWORD="
REM If PGPASSWORD is blank the job rebuilds files but SKIPS the ph_task publish (logged).
