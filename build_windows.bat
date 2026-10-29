@echo off
setlocal

echo ===================================================
echo   Voxel - Windows Standalone Package Builder
echo ===================================================

for /f "tokens=2 delims==" %%i in ('findstr "CURRENT_VERSION" src\utils\version.py') do set "RAW_VER=%%i"
set "VERSION=%RAW_VER:"=%"
set "VERSION=%VERSION: =%"
if not defined VERSION (
    echo [ERROR] Could not read CURRENT_VERSION from src\utils\version.py
    exit /b 1
)

set "PACKAGE_DIR=dist\Voxel-%VERSION%"
echo Building Voxel %VERSION% into %PACKAGE_DIR%...

pyinstaller --clean --noconfirm --onedir --windowed --name "Voxel" ^
    --distpath "%PACKAGE_DIR%" ^
    --workpath "build\windows-%VERSION%" ^
    --icon "assets\icon.ico" ^
    --collect-all edge_tts ^
    --collect-all certifi ^
    --collect-all PyQt6.QtMultimedia ^
    --hidden-import PyQt6.QtMultimedia ^
    --hidden-import pynput.keyboard._win32 ^
    --hidden-import pynput.mouse._win32 ^
    main.py

if errorlevel 1 (
    echo [ERROR] PyInstaller build failed.
    exit /b 1
)

copy /Y "%PACKAGE_DIR%\Voxel\Voxel.exe" "%PACKAGE_DIR%\Voxel\Voxel-%VERSION%.exe" >nul
if errorlevel 1 (
    echo [ERROR] Could not create the versioned executable.
    exit /b 1
)

if defined VOXEL_SIGN_CERT (
    if not defined VOXEL_SIGN_PASSWORD (
        echo [ERROR] VOXEL_SIGN_CERT is set but VOXEL_SIGN_PASSWORD is missing.
        exit /b 1
    )
    where signtool.exe >nul 2>nul
    if errorlevel 1 (
        echo [ERROR] signtool.exe is required when VOXEL_SIGN_CERT is set.
        exit /b 1
    )
    for /r "%PACKAGE_DIR%\Voxel" %%F in (*.exe *.dll) do (
        signtool sign /fd SHA256 /f "%VOXEL_SIGN_CERT%" /p "%VOXEL_SIGN_PASSWORD%" /tr https://timestamp.digicert.com /td SHA256 "%%F"
        if errorlevel 1 exit /b 1
    )
) else (
    echo [NOTICE] Package is unsigned. Set VOXEL_SIGN_CERT and VOXEL_SIGN_PASSWORD to sign all EXE and DLL files.
)

echo ===================================================
echo   BUILD COMPLETE
echo   Package folder: %PACKAGE_DIR%\Voxel
echo   Distribute the entire Voxel folder, not only Voxel.exe.
echo ===================================================
