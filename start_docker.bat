@echo off
SETLOCAL EnableDelayedExpansion
TITLE Smarketer Pro - Dynamic Docker Launcher

:: Navigate to the root directory where docker-compose.yml is
cd /d "%~dp0"
cd ..

echo ===================================================
echo       🚀 Starting Smarketer Pro (Docker) 🚀
echo ===================================================
echo.

:: 1. Check if Docker is running
echo [INFO] Checking Docker status...
docker info >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker is not running or not in PATH.
    echo [HINT] Please start Docker Desktop and try again.
    echo.
    pause
    exit /b
)

:: 2. Find Available Ports
echo [INFO] Detecting available ports...

:: Default ports and retry settings
set FRONTEND_PORT=3000
set BACKEND_PORT=8000
set MAX_RETRIES=20
set RETRY_COUNT=0

:find_frontend
if !RETRY_COUNT! GEQ %MAX_RETRIES% (
    echo [ERROR] Could not find an available Frontend port after %MAX_RETRIES% attempts.
    pause
    exit /b
)
:: Look for exact match ":PORT " to avoid partial match (e.g. 3000 matching 30000)
netstat -ano | findstr LISTENING | findstr ":%FRONTEND_PORT% " >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [WARN] Port %FRONTEND_PORT% is occupied. Trying next...
    set /a FRONTEND_PORT+=1
    set /a RETRY_COUNT+=1
    goto find_frontend
)
echo [INFO] Frontend allocated to port: %FRONTEND_PORT%

set RETRY_COUNT=0
:find_backend
if !RETRY_COUNT! GEQ %MAX_RETRIES% (
    echo [ERROR] Could not find an available Backend port after %MAX_RETRIES% attempts.
    pause
    exit /b
)
netstat -ano | findstr LISTENING | findstr ":%BACKEND_PORT% " >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [WARN] Port %BACKEND_PORT% is occupied. Trying next...
    set /a BACKEND_PORT+=1
    set /a RETRY_COUNT+=1
    goto find_backend
)
echo [INFO] Backend allocated to port: %BACKEND_PORT%
echo.

:: 3. Export Environment Variables for Docker Compose
set FRONTEND_PORT=%FRONTEND_PORT%
set BACKEND_PORT=%BACKEND_PORT%
set API_URL=http://localhost:%BACKEND_PORT%

:: 4. Launch Containers
echo [INFO] Building and starting containers...
docker compose up --build -d

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] Docker encountered an error during startup.
    pause
    exit /b
)

echo.
echo [SUCCESS] Smarketer Pro is running.
echo [INFO] Local UI: http://localhost:%FRONTEND_PORT%
echo [INFO] API Server: http://localhost:%BACKEND_PORT%
echo.
echo [INFO] Opening browser and streaming logs for debugging...
echo [HINT] Press Ctrl+C to stop streaming logs.
echo.

:: 5. Open Browser
start http://localhost:%FRONTEND_PORT%

:: 6. Stream Logs
docker compose logs -f

echo.
echo [INFO] Shutting down containers...
docker compose down
echo [DONE]
pause
