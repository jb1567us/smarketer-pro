@echo off
SETLOCAL EnableDelayedExpansion
TITLE Smarketer Pro - Reflex Prototype Launcher

:: Navigate to the directory where the script is located
cd /d "%~dp0"

echo ===================================================
echo       🚀 Starting Smarketer Pro (Prototype) 🚀
echo ===================================================
echo.

:: 1. Virtual Environment Activation
:: Check in project dir first, then parent
if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Activating .venv...
    call .venv\Scripts\activate.bat
) else if exist "..\venv\Scripts\activate.bat" (
    echo [INFO] Activating venv...
    call ..\venv\Scripts\activate.bat
) else (
    echo [WARN] No virtual environment found. Using global Python.
)

:: 2. Check for Reflex
where reflex >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Reflex is not installed or not in PATH.
    echo [HINT] Try: pip install reflex
    pause
    exit /b
)

:: 3. Launch Application
echo [INFO] Launching Reflex app...
echo.

:: Ensure we are in the root directory (where rxconfig.py is) before running
if exist "..\rxconfig.py" (
    cd ..
)

reflex run

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] Reflex encountered an error during startup.
    pause
)

pause
