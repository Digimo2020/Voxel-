# Voxel - Windows One-Click Installer & Unblocker
# Installs Voxel to %LOCALAPPDATA%\Programs\Voxel, unblocks SmartScreen zone tags, and creates Start Menu & Desktop shortcuts.

$ErrorActionPreference = "Stop"

$AppName = "Voxel"
$Version = "1.1.11"
$Publisher = "Voxel Labs"
$Description = "Voxel - Instant AI Voice & Document Reader"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir

# Determine executable source
$SourceExe = $null
$Candidates = @(
    (Join-Path $RepoRoot "dist\Voxel.exe"),
    (Join-Path $RepoRoot "dist\Voxel-$Version.exe"),
    (Join-Path $RepoRoot "Voxel-$Version.exe"),
    (Join-Path $RepoRoot "Voxel.exe"),
    (Join-Path $ScriptDir "Voxel.exe")
)

foreach ($c in $Candidates) {
    if (Test-Path $c) {
        $SourceExe = $c
        break
    }
}

if (-not $SourceExe) {
    Write-Host "[ERROR] Could not find Voxel.exe in distribution directories." -ForegroundColor Red
    exit 1
}

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "   Installing $AppName $Version ($Publisher)" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan

# 1. Target Directory: %LOCALAPPDATA%\Programs\Voxel
$InstallDir = Join-Path $env:LOCALAPPDATA "Programs\$AppName"
if (-not (Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
}

$DestExe = Join-Path $InstallDir "Voxel.exe"
$DestIcon = Join-Path $InstallDir "icon.ico"

# Stop any running instances
Get-Process -Name "Voxel" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Milliseconds 300

# 2. Copy Executable & Icon
Write-Host "[1/4] Copying files to $InstallDir..." -ForegroundColor Green
Copy-Item -Path $SourceExe -Destination $DestExe -Force

$SourceIcon = Join-Path $RepoRoot "assets\icon.ico"
if (Test-Path $SourceIcon) {
    Copy-Item -Path $SourceIcon -Destination $DestIcon -Force
}

# 3. Strip Mark-of-the-Web (Zone.Identifier) so SmartScreen doesn't block local execution
Write-Host "[2/4] Removing Mark-of-the-Web (SmartScreen unblock)..." -ForegroundColor Green
Unblock-File -Path $DestExe -ErrorAction SilentlyContinue

# 4. Create Shortcuts (Desktop + Start Menu)
Write-Host "[3/4] Creating Desktop and Start Menu shortcuts..." -ForegroundColor Green
$WshShell = New-Object -ComObject WScript.Shell

# Desktop Shortcut
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$DesktopShortcut = $WshShell.CreateShortcut((Join-Path $DesktopPath "$AppName.lnk"))
$DesktopShortcut.TargetPath = $DestExe
$DesktopShortcut.WorkingDirectory = $InstallDir
$DesktopShortcut.Description = $Description
if (Test-Path $DestIcon) { $DesktopShortcut.IconLocation = "$DestIcon,0" }
$DesktopShortcut.Save()

# Start Menu Shortcut
$StartMenuPath = [Environment]::GetFolderPath("Programs")
$StartShortcut = $WshShell.CreateShortcut((Join-Path $StartMenuPath "$AppName.lnk"))
$StartShortcut.TargetPath = $DestExe
$StartShortcut.WorkingDirectory = $InstallDir
$StartShortcut.Description = $Description
if (Test-Path $DestIcon) { $StartShortcut.IconLocation = "$DestIcon,0" }
$StartShortcut.Save()

# 5. Register in Windows Add/Remove Programs (Registry)
Write-Host "[4/4] Registering in Windows Application Manager..." -ForegroundColor Green
$RegPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\$AppName"
if (-not (Test-Path $RegPath)) {
    New-Item -Path $RegPath -Force | Out-Null
}
Set-ItemProperty -Path $RegPath -Name "DisplayName" -Value "$AppName - Instant AI Voice"
Set-ItemProperty -Path $RegPath -Name "DisplayVersion" -Value $Version
Set-ItemProperty -Path $RegPath -Name "Publisher" -Value $Publisher
Set-ItemProperty -Path $RegPath -Name "InstallLocation" -Value $InstallDir
Set-ItemProperty -Path $RegPath -Name "DisplayIcon" -Value $DestExe
Set-ItemProperty -Path $RegPath -Name "UninstallString" -Value "powershell.exe -Command Remove-Item -Recurse -Force '$InstallDir'; Remove-Item -Force '$DesktopPath\$AppName.lnk'; Remove-Item -Force '$StartMenuPath\$AppName.lnk'; Remove-Item -Path '$RegPath' -Recurse -Force"

Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "   SETUP COMPLETE! $AppName is installed." -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan

# Launch Voxel
Start-Process -FilePath $DestExe
