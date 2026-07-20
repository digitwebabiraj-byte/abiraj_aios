@echo off
setlocal
REM ==== ERA monthly auto-refresh (REQ-14-D02) - runs headless, no MCP, no human ====
REM project_code ERA · eBay Return Analysis Dashboard.
REM Warehouse (ph_task publish target). Same temp_user account used by the ebpd/epc publishes.
set "PGHOST=149.28.134.54"
set "PGPORT=5435"
set "PGDATABASE=order_management_copy"
set "PGUSER=temp_user"
REM Ledsone DB (the DATA source, read-only) + all passwords come from the GIT-IGNORED secrets file.
REM Copy era_secrets.template.bat to era_secrets.bat and fill it in (LED_PG* + PGPASSWORD).
if exist "%~dp0era_secrets.bat" call "%~dp0era_secrets.bat"
python "%~dp0era_monthly_run.py" >> "%~dp0era_run.log" 2>&1
set RC=%ERRORLEVEL%
REM On success the Python already wrote an OK line; on any crash, record a FAILED line so a gap is never silent.
if not "%RC%"=="0" echo [%DATE% %TIME%]  FAILED (exit %RC%)  ^|  see era_run.log for the error >> "%~dp0era_status.txt"
REM ---- Desktop alert on failure / auto-clear on success ----
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0era_alert.ps1" -Rc %RC%
endlocal
