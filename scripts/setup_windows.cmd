@echo off
setlocal
cd /d "%~dp0"
set PYTHONUTF8=1
chcp 65001 >nul
py -3.13 --version >nul 2>&1
if errorlevel 1 (
    echo Install the provided Python 3.13 x64 installer first, then run this file again.
    if /I not "%~1"=="/nopause" pause
    exit /b 1
)
if not exist ".venv\Scripts\python.exe" py -3.13 -m venv .venv
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -m pip install --no-index --find-links "%~dp0wheels" integral-compass==0.4.0
if errorlevel 1 goto failed
".venv\Scripts\python.exe" minimal_case.py
if errorlevel 1 goto failed
".venv\Scripts\python.exe" failure_cases.py
if errorlevel 1 goto failed
echo Setup, minimal cases and expected failure outcomes passed.
if /I not "%~1"=="/nopause" pause
exit /b 0
:failed
echo Setup or a minimal case failed. Keep this window and copy the error message.
if /I not "%~1"=="/nopause" pause
exit /b 1
