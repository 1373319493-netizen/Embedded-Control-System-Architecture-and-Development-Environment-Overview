@echo off
setlocal
cd /d "%~dp0"
if exist config\local.cmd call config\local.cmd
if defined ROBOT_PYTHON_DIR set "PATH=%ROBOT_PYTHON_DIR%;%PATH%"
python scripts\task2.py %*
if errorlevel 1 goto failed
exit /b 0
:failed
echo Task 2 failed. See the message above.
pause
exit /b 1
