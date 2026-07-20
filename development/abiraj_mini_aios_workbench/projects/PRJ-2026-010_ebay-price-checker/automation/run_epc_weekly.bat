@echo off
setlocal
REM ==== EPC weekly auto-refresh (REQ-12) - runs headless, no MCP, no human ====
REM Warehouse (ph_task write) - password comes from epc_secrets.bat, never this tracked file.
set "PGHOST=149.28.134.54"
set "PGPORT=5435"
set "PGDATABASE=order_management_copy"
set "PGUSER=temp_user"
REM ledsone (price reads) + PGPASSWORD live in the git-ignored secrets file next to this .bat.
if exist "%~dp0epc_secrets.bat" call "%~dp0epc_secrets.bat"
python "%~dp0epc_weekly_run.py" %* >> "%~dp0epc_run.log" 2>&1
set RC=%ERRORLEVEL%
if not "%RC%"=="0" echo [%DATE% %TIME%]  FAILED (exit %RC%)  ^|  see epc_run.log >> "%~dp0epc_status.txt"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0epc_alert.ps1" -Rc %RC%
endlocal & exit /b %RC%
