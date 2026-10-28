@echo off
setlocal
title Text 2 Voice

:: Find python executable
set "PYTHON_EXE=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe"

if not exist "%PYTHON_EXE%" (
    set "PYTHON_EXE=python.exe"
)

echo Starting Text 2 Voice...
"%PYTHON_EXE%" "%~dp0main.py"
pause
