@echo off
title Create Desktop Shortcut - AcademiaPro
echo ============================================================
echo   Creating Windows Desktop Shortcut for AcademiaPro ERP...
echo ============================================================

set SCRIPT_DIR=%~dp0
set TARGET=%SCRIPT_DIR%START_ACADEMIAPRO.bat
set SHORTCUT=%USERPROFILE%\Desktop\AcademiaPro ERP.lnk

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT%'); $s.TargetPath = '%TARGET%'; $s.WorkingDirectory = '%SCRIPT_DIR%'; $s.WindowStyle = 1; $s.Description = 'AcademiaPro Enterprise College Management System'; $s.Save()"

if exist "%SHORTCUT%" (
    echo.
    echo [SUCCESS] Desktop shortcut created successfully!
    echo Look for 'AcademiaPro ERP' on your Desktop.
    echo Double-click it anytime to launch the software!
) else (
    echo.
    echo [NOTE] Could not create shortcut automatically. You can right-click START_ACADEMIAPRO.bat and select 'Send to -> Desktop'.
)
echo.
pause
