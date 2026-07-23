@echo off
setlocal
REM ==== ESNM monthly auto-refresh (REQ-16-D02) - runs headless, no MCP, no human ====
REM project_code esnm - eBay Slow Moving & No Moving Products.
REM Credentials resolve in this order (same chain as ERA / EPC / EPPA):
REM   1. esnm_secrets.bat next to this file (optional, git-ignored) - per-project override
REM   2. GLOBAL user environment variables                          - the normal case
REM      set up once via 05_documentation/capability/shared_db_credentials/
REM   3. the non-secret defaults below (host/port/db/user only - never a password)
REM
REM THIS REPORT NEEDS TWO DATABASES. PGxxx is the warehouse (traffic); LED_PGxxx is ledsone
REM (listings, sales, PPC). If either password is missing the run ABORTS before writing.
if exist "%~dp0esnm_secrets.bat" call "%~dp0esnm_secrets.bat"
if not defined PGHOST     set "PGHOST=149.28.134.54"
if not defined PGPORT     set "PGPORT=5435"
if not defined PGDATABASE set "PGDATABASE=order_management_copy"
if not defined PGUSER     set "PGUSER=temp_user"
REM No password default anywhere.

python "%~dp0esnm_monthly_run.py" %* >> "%~dp0esnm_run.log" 2>&1
set RC=%ERRORLEVEL%

REM On success the Python already wrote the status JSON; on any crash record a FAILED line so a
REM gap is never silent.
if not "%RC%"=="0" echo [%DATE% %TIME%]  FAILED (exit %RC%)  ^|  see esnm_run.log >> "%~dp0esnm_status.txt"

REM ---- Desktop alert on failure / auto-clear on success ----
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0esnm_alert.ps1" -Rc %RC%
endlocal
exit /b %RC%
