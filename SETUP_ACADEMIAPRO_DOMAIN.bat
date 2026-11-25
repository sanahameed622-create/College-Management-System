@echo off
title AcademiaPro - Domain Setup (academiapro.local)
echo ========================================================
echo   Setting up easy domain: http://academiapro.local:5000
echo ========================================================
echo.

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [!] Administrator privileges required.
    echo Requesting elevation...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

findstr /i "academiapro.local" "%SystemRoot%\System32\drivers\etc\hosts" >nul
if %errorlevel% equ 0 (
    echo [*] 'academiapro.local' is ALREADY configured in your hosts file!
) else (
    echo 127.0.0.1 academiapro.local >> "%SystemRoot%\System32\drivers\etc\hosts"
    echo 127.0.0.1 academiapro >> "%SystemRoot%\System32\drivers\etc\hosts"
    echo [SUCCESS] Added academiapro.local to Windows hosts!
)

echo.
echo ========================================================
echo You can now access your project with either easy URL:
echo   1. http://localhost:5000/academiapro   (Universal)
echo   2. http://academiapro.local:5000        (Branded Domain)
echo ========================================================
echo.
pause
