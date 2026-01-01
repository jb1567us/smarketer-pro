@echo off
TITLE B2B Outreach Tool Launcher
echo ===================================================
echo       🚀 Starting B2B Outreach Tool System 🚀
echo ===================================================
echo.

:: 1. Start Search Engine (SearXNG)
echo [1/2] Initializing SearXNG (Docker)...
if exist "searxng\docker-compose.yaml" (
    cd searxng
    docker compose up -d
    if %ERRORLEVEL% NEQ 0 (
        echo Warning: 'docker compose' failed. Trying 'docker-compose'...
        docker-compose up -d
    )
    cd ..
    echo SearXNG started.
) else (
    echo Warning: searxng\docker-compose.yaml not found. Skipping Docker start.
)

:: 2. Start Application
echo.
echo [2/2] Launching Streamlit App...
echo.
echo NOTE: Close this window to stop the server.
echo.

streamlit run src/app.py

pause
