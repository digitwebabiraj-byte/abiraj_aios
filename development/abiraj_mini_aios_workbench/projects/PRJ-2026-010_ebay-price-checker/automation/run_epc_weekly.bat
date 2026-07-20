@echo off
setlocal
REM ==== EPC weekly auto-refresh (REQ-12) - runs headless, no MCP, no human ====
REM Credentials resolve in this order:
REM   1. epc_secrets.bat next to this file (optional, git-ignored)  - per-project override
REM   2. GLOBAL user environment variables                          - the normal case
REM      set up once via 05_documentation/capability/shared_db_credentials/
REM   3. the non-secret defaults below (host/port/db/user only - never a password)
if exist "%~dp0epc_secrets.bat" call "%~dp0epc_secrets.bat"
if not defined PGHOST     set "PGHOST=149.28.134.54"
if not defined PGPORT     set "PGPORT=5435"
if not defined PGDATABASE set "PGDATABASE=order_management_copy"
if not defined PGUSER     set "PGUSER=temp_user"
REM No password default anywhere: if PGPASSWORD / LED_* are unset the run ABORTS before writing.
python "%~dp0epc_weekly_run.py" %* >> "%~dp0epc_run.log" 2>&1
set RC=%ERRORLEVEL%
if not "%RC%"=="0" echo [%DATE% %TIME%]  FAILED (exit %RC%)  ^|  see epc_run.log >> "%~dp0epc_status.txt"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0epc_alert.ps1" -Rc %RC%
endlocal & exit /b %RC%
