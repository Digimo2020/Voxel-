@echo off
setlocal
title Push Text 2 Voice to GitHub
cd /d "%~dp0"

echo ========================================================
echo   Push Text 2 Voice to GitHub
echo   Repository: https://github.com/Digimo2020/Voxel-.git
echo ========================================================
echo.

where git >nul 2>nul
if errorlevel 1 (
  echo ERROR: Git was not found on PATH. Install Git for Windows first.
  pause
  exit /b 1
)

git rev-parse --is-inside-work-tree >nul 2>nul
if errorlevel 1 (
  echo ERROR: This folder is not a Git working tree.
  pause
  exit /b 1
)

for /f "delims=" %%R in ('git remote get-url origin 2^>nul') do set "REMOTE=%%R"
if not defined REMOTE (
  echo ERROR: No origin remote is configured.
  echo Configure origin as https://github.com/Digimo2020/Voxel-.git
  pause
  exit /b 1
)

echo Remote origin: %REMOTE%
echo.
echo Checking current branch and working tree...
git status --short --branch
echo.
echo This helper will NOT create a commit or discard local changes.
echo Review and commit your changes first, then press a key to push.
pause

git push -u origin main
if errorlevel 1 (
  echo.
  echo Push failed. Check authentication, branch name, and remote changes.
  echo Do not force-push. Reconcile divergent history before trying again.
  pause
  exit /b 1
)

echo.
echo Push completed successfully.
pause
