@echo off
REM REQ-28-D02 - weekly Friday refresh of the Amazon Keyword YoY dashboard + merged Meshika page.
REM Credentials resolve: 1) akyp_secrets.bat (git-ignored)  2) GLOBAL user env vars (normal case)
REM   3) non-secret host/port/db/user defaults below (never a password).
setlocal
cd /d "%~dp0"

if exist "akyp_secrets.bat" call "akyp_secrets.bat"
if not defined LED_PGHOST     set "LED_PGHOST=169.58.91.229"
if not defined LED_PGPORT     set "LED_PGPORT=5432"
if not defined LED_PGDATABASE set "LED_PGDATABASE=ledsone"
if not defined LED_PGUSER     set "LED_PGUSER=dev_user"
if not defined PGHOST         set "PGHOST=149.28.134.54"
if not defined PGPORT         set "PGPORT=5435"
if not defined PGDATABASE     set "PGDATABASE=order_management_copy"
if not defined PGUSER         set "PGUSER=temp_user"
REM No password default: if LED_PGPASSWORD / PGPASSWORD are unset the run ABORTS before writing.

python "akyp_weekly_run.py" %*
set RC=%ERRORLEVEL%

if not "%RC%"=="0" (
  echo [AKYP] run FAILED with code %RC% - raising desktop alert
  powershell -NoProfile -ExecutionPolicy Bypass -File "akyp_alert.ps1"
)
set "LED_PGPASSWORD="
set "PGPASSWORD="
exit /b %RC%
