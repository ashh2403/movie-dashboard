@echo off
REM ============================================================
REM  Movie Industry Performance Dashboard - one-click start
REM  Double-click this file. The first run installs everything
REM  (needs internet, about 2-3 minutes); later runs start fast.
REM ============================================================
cd /d "%~dp0"
title Movie Industry Performance Dashboard

if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Creating virtual environment...
    py -3 -m venv .venv 2>nul || python -m venv .venv
    if errorlevel 1 (
        echo.
        echo Python was not found. Install Python 3.10+ from https://www.python.org/downloads/
        echo and tick "Add python.exe to PATH" during installation.
        pause
        exit /b 1
    )
)

echo [2/3] Installing / checking requirements...
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -q -r requirements.txt
if errorlevel 1 (
    echo Installing requirements failed. Check your internet connection and try again.
    pause
    exit /b 1
)

echo [3/3] Starting the dashboard at http://localhost:8501  (close this window to stop)
".venv\Scripts\python.exe" -m streamlit run app.py --server.headless false
pause
