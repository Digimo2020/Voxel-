@echo off
setlocal enabledelayedexpansion

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
pyinstaller --noconfirm --onefile --windowed --name "Voxel" ^
    --icon "assets/icon.ico" ^
    --collect-all edge_tts ^
    --collect-all certifi ^
    --hidden-import pynput.keyboard._win32 ^
    --hidden-import pynput.mouse._win32 ^
    main.py

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] PyInstaller build failed!
    exit /b %ERRORLEVEL%
)

:: 4. Archive versioned executable (preserving previous versions in dist\)
copy /Y "dist\Voxel.exe" "dist\Voxel-%VERSION%.exe"

echo ===================================================
echo   BUILD COMPLETE!
echo   - Latest Executable   : dist\Voxel.exe
echo   - Versioned Executable: dist\Voxel-%VERSION%.exe
echo   - All previous versions preserved in dist\
echo ===================================================
dir dist\*.exe
pause
