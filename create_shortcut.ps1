$desktopPath = [Environment]::GetFolderPath("Desktop")
$publicDesktop = [Environment]::GetFolderPath("CommonDesktopDirectory")
$targetPath = "C:\Users\Sana Hameed Hacker\Downloads\college_management_system\START_ACADEMIAPRO.bat"
$workingDir = "C:\Users\Sana Hameed Hacker\Downloads\college_management_system"

$ws = New-Object -ComObject WScript.Shell

# 1. Active User Desktop (OneDrive Desktop)
$shortcutPath1 = Join-Path $desktopPath "AcademiaPro ERP.lnk"
$s1 = $ws.CreateShortcut($shortcutPath1)
$s1.TargetPath = $targetPath
$s1.WorkingDirectory = $workingDir
$s1.Description = "AcademiaPro Enterprise College Management System"
$s1.Save()
Write-Host "Created on Active Desktop: $shortcutPath1"

# 2. Local User Desktop (C:\Users\...\Desktop)
$localDesktop = "C:\Users\Sana Hameed Hacker\Desktop"
if (Test-Path $localDesktop) {
    $shortcutPath2 = Join-Path $localDesktop "AcademiaPro ERP.lnk"
    $s2 = $ws.CreateShortcut($shortcutPath2)
    $s2.TargetPath = $targetPath
    $s2.WorkingDirectory = $workingDir
    $s2.Description = "AcademiaPro Enterprise College Management System"
    $s2.Save()
    Write-Host "Created on Local Desktop: $shortcutPath2"
}
