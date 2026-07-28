@echo off
setlocal
cd /d "%~dp0"
REM Load git-ignored secrets if present; otherwise rely on the shared global env store.
if exist "%~dp0eppr_secrets.bat" call "%~dp0eppr_secrets.bat"
python "%~dp0eppr_monthly_run.py"
if errorlevel 1 (
  powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0eppr_alert.ps1"
  exit /b 1
)
exit /b 0
