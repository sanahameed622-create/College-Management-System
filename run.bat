@echo off
echo ========================================================
echo   AcademiaPro - College Management System Launcher
echo ========================================================
cd /d "%~dp0"

echo [*] Initializing Database...
python database\init_db.py

echo.
echo [*] Launching Web Application on http://localhost:5000/academiapro ...
echo [*] Easy Project URL : http://localhost:5000/academiapro
echo [*] Local Domain URL : http://academiapro.local:5000
echo [i] Press Ctrl+C to terminate the server.
python app\app.py
pause
