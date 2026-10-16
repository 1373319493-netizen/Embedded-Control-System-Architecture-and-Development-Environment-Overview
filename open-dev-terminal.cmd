@echo off
setlocal
set "ROBOT_ROOT=%~dp0"
if exist "%ROBOT_ROOT%config\local.cmd" call "%ROBOT_ROOT%config\local.cmd"
if defined ROBOT_PYTHON_DIR set "PATH=%ROBOT_PYTHON_DIR%;%PATH%"
if defined ARM_GCC_BIN set "PATH=%ARM_GCC_BIN%;%PATH%"
if defined QEMU_BIN set "PATH=%QEMU_BIN%;%PATH%"
if defined QEMU_STM32_BIN set "PATH=%QEMU_STM32_BIN%;%PATH%"
if defined NINJA_BIN set "PATH=%NINJA_BIN%;%PATH%"
if defined CMAKE_BIN set "PATH=%CMAKE_BIN%;%PATH%"
if defined ROBOT_TEMP set "TEMP=%ROBOT_TEMP%"
if defined ROBOT_TEMP set "TMP=%ROBOT_TEMP%"
cd /d "%ROBOT_ROOT%"
if /i "%~1"=="--verify" goto verify
echo Robot development environment ready.
echo Run: python scripts\verify_environment.py
cmd /k
exit /b
:verify
python scripts\verify_environment.py
exit /b %errorlevel%
