@echo off
setlocal
title Voxel - Text to Speech, Anywhere

cd /d "%~dp0"

:: 1. Check if python is in PATH
where python >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PYTHON_EXE=python"
    goto :run
)

:: 2. Check standard Python installation locations
if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
    goto :run
)
if exist "%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe"
    goto :run
)
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    goto :run
)

set "PYTHON_EXE=python.exe"

:run
echo Starting Voxel...
"%PYTHON_EXE%" "%~dp0main.py"
if %ERRORLEVEL% neq 0 pause
