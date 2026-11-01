@echo off
setlocal
title CSIR Secure Web Appliance OS - Testbed VM Launcher

echo ==============================================================================
echo  CSIR SECURE WEB APPLIANCE OS (CSIR-SWA OS) - TESTBED VM LAUNCHER
echo ==============================================================================
echo.

:: Check for Administrator elevation
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] WARNING: You are not running as Administrator.
    echo     If VirtualBox drivers are not registered, please right-click this .bat
    echo     and select "Run as administrator".
    echo.
)

echo Select deployment mode:
echo   [1] GUI Mode      (Interactive Graphical Window - Recommended)
echo   [2] Headless Mode (Background Service)
echo   [3] Capture Screenshot of Running Console
echo   [4] Stop / Poweroff Testbed VM
echo   [5] Launch Mock Web Management Console Testbed (Local http://localhost:8443)
echo.

set /p choice="Enter choice [1-5] (default=1): "
if "%choice%"=="" set choice=1

if "%choice%"=="1" (
    powershell -ExecutionPolicy Bypass -File "%~dp0deploy_testbed_vm.ps1" -Mode gui
) else if "%choice%"=="2" (
    powershell -ExecutionPolicy Bypass -File "%~dp0deploy_testbed_vm.ps1" -Mode headless
) else if "%choice%"=="3" (
    powershell -ExecutionPolicy Bypass -File "%~dp0deploy_testbed_vm.ps1" -Mode screenshot
) else if "%choice%"=="4" (
    powershell -ExecutionPolicy Bypass -File "%~dp0deploy_testbed_vm.ps1" -Mode stop
) else if "%choice%"=="5" (
    python "%~dp0scripts\generate_web_console_screenshots.py"
) else (
    echo Invalid choice.
)

pause
