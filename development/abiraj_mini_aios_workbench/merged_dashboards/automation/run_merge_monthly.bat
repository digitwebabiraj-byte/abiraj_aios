@echo off
REM Merge dashboard monthly run — refresh live (EPPR+ESNM) -> build unified HTML.
REM Credentials come from the GLOBAL user environment (LED_PGPASSWORD + PGPASSWORD);
REM non-secret coordinates default below (same as the fleet). No password here.
setlocal
cd /d "%~dp0"
if not defined LED_PGHOST     set "LED_PGHOST=169.58.91.229"
if not defined LED_PGPORT     set "LED_PGPORT=5432"
if not defined LED_PGDATABASE set "LED_PGDATABASE=ledsone"
if not defined LED_PGUSER     set "LED_PGUSER=dev_user"
if not defined PGHOST         set "PGHOST=149.28.134.54"
if not defined PGPORT         set "PGPORT=5435"
if not defined PGDATABASE     set "PGDATABASE=order_management_copy"
if not defined PGUSER         set "PGUSER=temp_user"
python "%~dp0merge_monthly_run.py" %* >> "%~dp0merge_run.log" 2>&1
set RC=%ERRORLEVEL%
if not "%RC%"=="0" echo [MERGE] run FAILED with exit code %RC% - see merge_run.log >&2
exit /b %RC%
