@echo off
title AcademiaPro - Automated Project Backup
color 0A
echo ============================================================
echo   ACADEMIAPRO - AUTOMATED BACKUP & PROTECTION TOOL
echo ============================================================
echo.
cd /d "%~dp0"

for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TIMESTAMP=%datetime:~0,8%_%datetime:~8,4%
set BACKUP_NAME=AcademiaPro_Backup_%TIMESTAMP%.zip
set BACKUP_DEST=%USERPROFILE%\Desktop\%BACKUP_NAME%

echo [*] Archiving complete project files, database, and documentation...
powershell -Command "Compress-Archive -Path 'app', 'database', 'docs', 'academiapro.db', 'desktop_launcher.py', 'START_ACADEMIAPRO.bat', 'requirements.txt', 'test_app.py', 'README.md' -DestinationPath '%BACKUP_DEST%' -Force"

if exist "%BACKUP_DEST%" (
    echo.
    echo ============================================================
    echo [SUCCESS] Complete Project Backup Created Successfully!
    echo Location: %BACKUP_DEST%
    echo ============================================================
    echo You can copy this ZIP file to your USB Drive or Google Drive!
) else (
    echo [ERROR] Backup creation failed. Please check folder permissions.
)
echo.
pause
