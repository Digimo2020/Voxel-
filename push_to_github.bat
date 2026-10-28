@echo off
title Push Text 2 Voice to GitHub
cd /d "%~dp0"

echo ==============================================
echo Pushing Text 2 Voice to https://github.com/Digimo2020/Text-2-Voice.git
echo ==============================================
echo.

"C:\Users\%USERNAME%\AppData\Local\Programs\Git\cmd\git.exe" push -u origin main

echo.
echo If you saw a login popup, please authorize GitHub to complete the push.
echo.
pause
