@echo off
title AcademiaPro - Enterprise College Management System
color 0B
echo ============================================================
echo   ACADEMIAPRO - ENTERPRISE COLLEGE MANAGEMENT SYSTEM (v2.0)
echo   Intermediate (1st/2nd Year) + BS Degree Management
echo ============================================================
echo.
echo [*] Checking Environment & Database...
cd /d "%~dp0"

REM Verify Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.10+ from python.org
    pause
    exit /b 1
)

echo [*] Launching AcademiaPro Native Desktop Software...
python desktop_launcher.py

pause
