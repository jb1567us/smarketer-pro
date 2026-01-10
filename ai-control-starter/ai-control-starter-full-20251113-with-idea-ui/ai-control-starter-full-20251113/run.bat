@echo off
echo ============================================
echo      AI Control Starter - Run Menu
echo ============================================
echo.
echo   1. Bootstrap team and questions (from idea.txt)
echo   2. Open Q&A web UI (fill answers in browser)
echo   3. Generate control.md from your answers
echo   4. Exit
echo.

set /p choice=Enter choice (1-4): 

if "%choice%"=="1" goto bootstrap
if "%choice%"=="2" goto ui
if "%choice%"=="3" goto control
if "%choice%"=="4" goto end

echo.
echo Invalid choice. Please run run.bat again and choose 1-4.
goto end

:bootstrap
echo.
echo Running bootstrap_team_and_questions.py ...
python scripts\bootstrap_team_and_questions.py --idea idea.txt
echo.
pause
goto end

:ui
echo.
echo Starting Q&A web UI...
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

:end
