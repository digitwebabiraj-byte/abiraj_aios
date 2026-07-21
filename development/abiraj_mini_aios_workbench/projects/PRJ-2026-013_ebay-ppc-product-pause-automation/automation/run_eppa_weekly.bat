@echo off
REM REQ-15-D02 — weekly Monday refresh of the eBay PPC Pause Automation report.
REM Credentials resolve in this order (same as PRJ-2026-010 / 011 / 012):
REM   1. eppa_secrets.bat next to this file (optional, git-ignored)  - per-project override
REM   2. GLOBAL user environment variables                           - the normal case
REM      set up once via 05_documentation/capability/shared_db_credentials/
REM   3. the non-secret defaults below (host/port/db/user only - never a password)
setlocal
cd /d "%~dp0"

if exist "eppa_secrets.bat" call "eppa_secrets.bat"
if not defined LED_PGHOST     set "LED_PGHOST=207.148.78.148"
if not defined LED_PGPORT     set "LED_PGPORT=5432"
if not defined LED_PGDATABASE set "LED_PGDATABASE=ledsone"
if not defined LED_PGUSER     set "LED_PGUSER=dbhub_readonly"
if not defined PGHOST         set "PGHOST=149.28.134.54"
if not defined PGPORT         set "PGPORT=5435"
if not defined PGDATABASE     set "PGDATABASE=order_management_copy"
if not defined PGUSER         set "PGUSER=temp_user"
REM No password default anywhere: if LED_PGPASSWORD / PGPASSWORD are unset the run ABORTS
REM before writing - eppa_weekly_run.py checks both up front.

python "eppa_weekly_run.py" %*
set RC=%ERRORLEVEL%

if not "%RC%"=="0" (
  echo [EPPA] run FAILED with code %RC% - raising desktop alert
  powershell -NoProfile -ExecutionPolicy Bypass -File "eppa_alert.ps1"
)

REM Clear the credentials from this shell's environment.
set "LED_PGPASSWORD="
exit /b %RC%
