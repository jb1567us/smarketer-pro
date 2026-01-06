@echo off
echo ============================================
echo      AI Control Starter - Run Menu
echo ============================================
echo.
echo   1. (Optional / legacy) Bootstrap team and questions from idea.txt via CLI
echo   2. Open web UI (enter idea + fill answers in browser)
echo   3. Generate control.md from your answers
echo   4. Auto-create role-specific generator scripts  
echo   5. Auto-configure models with Ollama
echo   6. Open Unified Dashboard (All features + Auto-Updating Chat!) [NEW]
echo   7. Exit
echo.

set /p choice=Enter choice (1-7): 

if "%choice%"=="1" goto bootstrap
if "%choice%"=="2" goto ui
if "%choice%"=="3" goto control
if "%choice%"=="4" goto gens
if "%choice%"=="5" goto models
if "%choice%"=="6" goto dashboard
if "%choice%"=="7" goto end

echo.
echo Invalid choice. Please run run.bat again and choose 1-7.
goto end

:bootstrap
echo.
echo (Optional) Running bootstrap_team_and_questions.py ...
echo NOTE: This requires idea.txt to already exist and is not needed if you use the web UI.
python scripts\bootstrap_team_and_questions.py --idea idea.txt
echo.
pause
goto end

:ui
echo.
echo Starting web UI...
echo It will first ask for your idea, then guide you to the questions screen.
echo Open your browser to http://127.0.0.1:5000
echo Press CTRL+C in this window to stop the server.
echo.
python scripts\qna_web.py
goto end

:control
echo.
echo Generating control.md from your answers...
echo Using FAST template-based generation (instant)...
python scripts\generate_control_doc_fast.py --idea idea.txt
echo.
echo control.md has been generated successfully!
echo.
pause
goto end

:gens
echo.
echo Auto-creating role-specific generator scripts from team_and_questions_v0.1.json ...
python scripts\auto_create_role_generators.py
echo.
pause
goto end

:models
echo.
echo Auto-configuring models based on your hardware and Ollama...
python scripts\auto_configure_models.py
echo.
pause
goto end

:dashboard
echo.
echo ============================================
echo      Starting Unified Dashboard
echo ============================================
echo.
echo 🚀 ALL FEATURES IN ONE PLACE!
echo.
echo ✅ View all project artifacts
echo ✅ Generate everything from one interface  
echo ✅ Interactive chat with AUTO-UPDATES
echo ✅ Questions page integrated
echo ✅ No more switching between options
echo.
echo Opening browser to http://127.0.0.1:5000
echo Press CTRL+C in this window to stop the server.
echo.
python scripts\dashboard.py
goto end

:end