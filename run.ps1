Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  AcademiaPro - College Management System Launcher" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

$CurrentDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $CurrentDir

Write-Host "[*] Initializing Database..." -ForegroundColor Yellow
python database\init_db.py

Write-Host "`n[*] Starting Application Server on http://127.0.0.1:5000 ..." -ForegroundColor Green
Write-Host "[i] Press Ctrl+C in this terminal to stop the server.`n" -ForegroundColor Gray
python app\app.py
