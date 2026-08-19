@echo off
setlocal
cd /d "%~dp0"
REM Load git-ignored secrets if present; otherwise rely on the shared global env store.
if exist "%~dp0bgct_secrets.bat" call "%~dp0bgct_secrets.bat"
python "%~dp0bgct_monthly_run.py"
if errorlevel 1 (
  powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0bgct_alert.ps1"
  exit /b 1
)
exit /b 0
