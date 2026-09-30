@echo off
setlocal
cd /d "%~dp0backend"

if not exist ".venv\Scripts\python.exe" (
  echo [ERROR] Python virtual environment not found at backend\.venv
  echo Create it first with: py -m venv .venv
  exit /b 1
)

echo =============================================
echo Tower Time-Lapse System v1.0.1 - Windows Test
 echo =============================================

".venv\Scripts\python.exe" -m pytest -q
if errorlevel 1 exit /b %errorlevel%

echo.
echo Running Integration / E2E regression...
".venv\Scripts\python.exe" -m pytest -q -m "integration or e2e" tests\test_phase17_integration_e2e.py
if errorlevel 1 exit /b %errorlevel%

echo.
echo ALL TESTS PASSED.
endlocal
