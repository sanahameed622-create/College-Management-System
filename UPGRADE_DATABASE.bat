@echo off
title AcademiaPro Database Upgrader
color 0A
echo ============================================================
echo   ACADEMIAPRO - DATABASE UPGRADE & MULTI-TIER MIGRATOR
echo ============================================================
echo.
cd /d "%~dp0"
python database\upgrade_to_v2.py
echo.
echo [DONE] Database is updated and ready!
pause
