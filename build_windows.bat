@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

echo ===================================================
echo   Voxel - Windows Standalone Executable Builder
echo ===================================================

:: 1. Extract Current Version
for /f "tokens=2 delims==" %%i in ('findstr "CURRENT_VERSION" src\utils\version.py') do (
    set RAW_VER=%%i
)
:: Trim quotes and spaces
set VERSION=%RAW_VER:"=%
set VERSION=%VERSION: =%

echo Building Voxel %VERSION% for Windows...

:: 2. Stop any running Voxel instances
taskkill /F /IM Voxel.exe 2>nul
taskkill /F /IM Voxel-%VERSION%.exe 2>nul

:: 3. Run PyInstaller
python -m PyInstaller --noconfirm --onefile --windowed --name "Voxel" ^
    --icon "assets/icon.ico" ^
    --version-file "file_version_info.txt" ^
    --add-data "assets;assets" ^
    --collect-all edge_tts ^
    --collect-all certifi ^
    --collect-all pypdf ^
    --hidden-import pynput.keyboard._win32 ^
    --hidden-import pynput.mouse._win32 ^
    --exclude-module PyQt6.QtMultimedia ^
    --exclude-module PyQt6.QtMultimediaWidgets ^
    --exclude-module PyQt6.QtQml ^
    --exclude-module PyQt6.QtQuick ^
    --exclude-module PyQt6.QtSql ^
    --exclude-module PyQt6.QtTest ^
    --exclude-module PyQt6.QtXml ^
    main.py

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] PyInstaller build failed!
    exit /b %ERRORLEVEL%
)

:: 4. Archive versioned executable (preserving previous versions in dist\)
copy /Y "dist\Voxel.exe" "dist\Voxel-%VERSION%.exe"

echo ===================================================
echo   BUILD COMPLETE!
echo   Output: dist\Voxel.exe and dist\Voxel-%VERSION%.exe
echo ===================================================
