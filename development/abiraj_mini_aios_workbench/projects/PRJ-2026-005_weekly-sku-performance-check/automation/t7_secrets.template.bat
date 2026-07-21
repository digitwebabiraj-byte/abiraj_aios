@echo off
REM ==== T7 credentials (OPTIONAL) ====
REM You normally do NOT need this file. The global credential store
REM (05_documentation\capability\shared_db_credentials\) already supplies PGPASSWORD.
REM
REM Only use this if T7 must connect as a DIFFERENT account from the other projects.
REM Fill it in, then SAVE THIS FILE AS:  t7_secrets.bat   (that name is git-ignored)
REM The real password never gets committed.

REM --- warehouse (READ the orders/listings + WRITE ph_task only) ---
REM Host/port/db/user come from run_t7_weekly.bat's non-secret defaults; override only if needed.
set "PGPASSWORD="
