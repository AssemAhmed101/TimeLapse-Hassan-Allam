\
@echo off
setlocal
cd /d "%~dp0"
start "Time-Lapse Backend" cmd /k "windows-start-backend.cmd"
timeout /t 2 /nobreak >nul
start "Time-Lapse Dashboard" cmd /k "windows-start-dashboard.cmd"
echo Backend and Dashboard windows started.
endlocal
