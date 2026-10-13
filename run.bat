@echo off
echo ========================================================
echo   AcademiaPro - College Management System Launcher
echo ========================================================
cd /d "%~dp0"

echo [*] Initializing Database...
python database\init_db.py

echo.
echo [*] Launching Web Application on http://127.0.0.1:5000 ...
echo [i] Press Ctrl+C to terminate the server.
python app\app.py
pause
