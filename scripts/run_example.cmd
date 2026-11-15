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
".venv\Scripts\python.exe" minimal_case.py
set example_exit=%errorlevel%
pause
exit /b %example_exit%
