@echo off
title Nessus Bulk Downloader
echo.
echo ============================================
echo   Nessus Bulk Downloader - Web UI
echo ============================================
echo.

:: Check Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+ from https://python.org
    echo         Make sure to check "Add Python to PATH" during install.
    pause
    exit /b 1
)

:: Install dependencies if needed
echo Checking dependencies...
pip show flask requests >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies.
        pause
        exit /b 1
    )
)

echo.
echo Starting server... Open http://localhost:5000 in your browser
echo Press Ctrl+C to stop.
echo.
python nessus_bulk_downloader.py
pause
