@echo off
cd /d "%~dp0"
echo ===================================================
echo   Installing Voxel for Windows...
echo ===================================================
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\install_windows.ps1"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Installation failed with error code %ERRORLEVEL%.
    pause
)
