@echo off
setlocal
if not exist "%~dp0.venv\Scripts\python.exe" (
  echo Run setup.ps1 first.
  exit /b 1
)
"%~dp0.venv\Scripts\python.exe" -m athis_autopilot %*
exit /b %ERRORLEVEL%
