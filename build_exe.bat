@echo off
title Build Voxel Standalone EXE
cd /d "%~dp0"

echo ==============================================
echo Building Standalone Voxel.exe
echo ==============================================
echo.

python -m PyInstaller --noconfirm --onefile --windowed --name "Voxel" ^
    --icon "assets/icon.ico" ^
    --collect-all edge_tts ^
    --collect-all certifi ^
    --hidden-import pynput.keyboard._win32 ^
    --hidden-import pynput.mouse._win32 ^
    main.py

echo.
if exist "dist\Voxel.exe" (
    echo ==============================================
    echo SUCCESS! Standalone executable generated:
    echo %~dp0dist\Voxel.exe
    echo ==============================================
) else (
    echo Build failed. Please check the logs above.
)
echo.
pause
