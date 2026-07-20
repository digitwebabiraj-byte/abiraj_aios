@echo off
setlocal
REM ==== EBPD weekly auto-refresh (REQ-13-D02) - runs headless, no MCP, no human ====
REM Warehouse (reads + ph_task write). Same account already used by push_ebpd_dashboard.py.
set "PGHOST=149.28.134.54"
set "PGPORT=5435"
set "PGDATABASE=order_management_copy"
set "PGUSER=temp_user"
REM PGPASSWORD is provided by ebpd_secrets.bat (git-ignored) so no password lives in this tracked file.
REM Ledsone DB (New Listings) - kept in a GIT-IGNORED secrets file next to this .bat.
REM Copy ebpd_secrets.template.bat to ebpd_secrets.bat and fill in the ledsone connection.
if exist "%~dp0ebpd_secrets.bat" call "%~dp0ebpd_secrets.bat"
python "%~dp0ebpd_weekly_run.py" >> "%~dp0ebpd_run.log" 2>&1
set RC=%ERRORLEVEL%
REM On success the Python already wrote an OK line; on any crash, record a FAILED line so a gap is never silent.
if not "%RC%"=="0" echo [%DATE% %TIME%]  FAILED (exit %RC%)  ^|  see ebpd_run.log for the error >> "%~dp0ebpd_status.txt"
REM ---- Desktop alert on failure / auto-clear on success (all logic in ebpd_alert.ps1) ----
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0ebpd_alert.ps1" -Rc %RC%
endlocal
