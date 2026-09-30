@echo off
setlocal
cd /d "%~dp0backend"
if not exist ".venv\Scripts\python.exe" (
  echo [ERROR] backend\.venv not found.
  exit /b 1
)
".venv\Scripts\python.exe" scripts\create_admin.py
endlocal
