@echo off
echo ============================================
echo      AI Control Starter - Run Menu
echo ============================================
echo.
echo   1. (Optional / legacy) Bootstrap team and questions from idea.txt via CLI
echo   2. Open web UI (enter idea + fill answers in browser)  [RECOMMENDED]
echo   3. Generate control.md from your answers
echo   4. Auto-create role-specific generator scripts
echo   5. Exit
echo.

set /p choice=Enter choice (1-5): 

if "%choice%"=="1" goto bootstrap
if "%choice%"=="2" goto ui
if "%choice%"=="3" goto control
if "%choice%"=="4" goto gens
if "%choice%"=="5" goto end

echo.
echo Invalid choice. Please run run.bat again and choose 1-5.
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
python scripts\generate_control_doc.py --idea idea.txt
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

:end
