@echo off
setlocal
cd /d "%~dp0backend"
if not exist ".venv\Scripts\python.exe" (
  echo [ERROR] backend\.venv not found.
  exit /b 1
)
".venv\Scripts\python.exe" -m alembic upgrade head
if errorlevel 1 exit /b %errorlevel%
".venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000
endlocal
