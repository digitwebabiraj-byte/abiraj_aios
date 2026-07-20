@echo off
setlocal
REM ==== EBPD weekly auto-refresh (REQ-13-D02) - runs headless, no MCP, no human ====
REM Credentials resolve in this order (same as PRJ-2026-010 / EPC):
REM   1. ebpd_secrets.bat next to this file (optional, git-ignored)  - per-project override
REM   2. GLOBAL user environment variables                           - the normal case
REM      set up once via 05_documentation/capability/shared_db_credentials/
REM   3. the non-secret defaults below (host/port/db/user only - never a password)
if exist "%~dp0ebpd_secrets.bat" call "%~dp0ebpd_secrets.bat"
if not defined PGHOST     set "PGHOST=149.28.134.54"
if not defined PGPORT     set "PGPORT=5435"
if not defined PGDATABASE set "PGDATABASE=order_management_copy"
if not defined PGUSER     set "PGUSER=temp_user"
REM No password default anywhere: if PGPASSWORD / LED_* are unset the run ABORTS before writing.
python "%~dp0ebpd_weekly_run.py" %* >> "%~dp0ebpd_run.log" 2>&1
set RC=%ERRORLEVEL%
REM On success the Python already wrote an OK line; on any crash, record a FAILED line so a gap is never silent.
if not "%RC%"=="0" echo [%DATE% %TIME%]  FAILED (exit %RC%)  ^|  see ebpd_run.log for the error >> "%~dp0ebpd_status.txt"
REM ---- Desktop alert on failure / auto-clear on success (all logic in ebpd_alert.ps1) ----
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0ebpd_alert.ps1" -Rc %RC%
endlocal
