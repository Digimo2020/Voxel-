@echo off
title Push Text 2 Voice to GitHub
cd /d "%~dp0"

echo ========================================================
echo   Push Text 2 Voice to GitHub
echo   Repository: https://github.com/Digimo2020/Text-2-Voice.git
echo ========================================================
echo.
echo Choose an authentication method:
echo   [1] Interactive Browser Login (Recommended - uses Git Credential Manager)
echo   [2] GitHub Personal Access Token (PAT)
echo.
set /p choice="Enter choice (1 or 2, default is 1): "

if "%choice%"=="2" goto use_token
goto use_gcm

:use_gcm
echo.
echo Launching Git push...
echo A GitHub authorization window will open in your browser.
echo Please click "Authorize" or "Sign in with browser" to complete the push.
echo.
"C:\Users\%USERNAME%\AppData\Local\Programs\Git\cmd\git.exe" push -u origin main
goto end

:use_token
echo.
set /p token="Paste your GitHub Personal Access Token (classic with 'repo' scope): "
if "%token%"=="" (
    echo No token provided. Aborting.
    goto end
)
echo Pushing with access token...
"C:\Users\%USERNAME%\AppData\Local\Programs\Git\cmd\git.exe" push -u https://%token%@github.com/Digimo2020/Text-2-Voice.git main
goto end

:end
echo.
echo ========================================================
pause
