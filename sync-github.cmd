@echo off
setlocal
cd /d "%~dp0"
echo Pushing committed changes to GitHub...
git -c http.proxy= push -u origin main
if errorlevel 1 goto failed
echo.
echo GitHub sync completed.
pause
exit /b 0
:failed
echo.
echo Sync failed. Complete GitHub sign-in if requested, then retry.
echo If the remote has new commits, fetch and review them before pushing.
pause
exit /b 1
