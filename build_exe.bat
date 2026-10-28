@echo off
title Build Text 2 Voice Standalone EXE
cd /d "%~dp0"

echo ==============================================
echo Building Standalone Text2Voice.exe
echo ==============================================
echo.

set "PYINSTALLER=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\Scripts\pyinstaller.exe"

if not exist "%PYINSTALLER%" (
    set "PYINSTALLER=pyinstaller"
)

"%PYINSTALLER%" --noconfirm --onefile --windowed --name "Text2Voice" ^
    --collect-all edge_tts ^
    --collect-all certifi ^
    --collect-all pygame ^
    --hidden-import pynput.keyboard._win32 ^
    --hidden-import pynput.mouse._win32 ^
    main.py

echo.
if exist "dist\Text2Voice.exe" (
    echo ==============================================
    echo SUCCESS! Standalone executable generated:
    echo %~dp0dist\Text2Voice.exe
    echo ==============================================
) else (
    echo Build failed. Please check the logs above.
)
echo.
pause
