@echo off
setlocal
cd /d "%~dp0"
set PYTHONUTF8=1
chcp 65001 >nul
if not exist ".venv\Scripts\python.exe" (
    echo Run setup_windows.cmd first.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" failure_cases.py %*
set failure_exit=%errorlevel%
pause
exit /b %failure_exit%
