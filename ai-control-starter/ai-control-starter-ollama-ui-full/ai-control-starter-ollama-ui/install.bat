@echo off
echo ============================================
echo   AI Control Starter - Install Dependencies
echo ============================================
echo.

python -m pip install --upgrade pip
IF %ERRORLEVEL% NEQ 0 (
    echo Failed to upgrade pip. Make sure Python is installed and on PATH.
    pause
    goto :EOF
)

pip install -r requirements.txt
IF %ERRORLEVEL% NEQ 0 (
    echo Failed to install requirements. Check the error messages above.
    pause
    goto :EOF
)

echo.
echo Dependencies installed successfully.
echo You can now run run.bat to use the tools.
echo.
pause
