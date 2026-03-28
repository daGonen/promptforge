@echo off
title PromptForge — Installer
color 0A

echo.
echo  ==========================================
echo   PromptForge  by daGonen
echo   First-time setup
echo  ==========================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found.
    echo  Please install Python 3.10 or later from https://python.org
    echo  Make sure to check "Add Python to PATH" during install.
    echo.
    pause
    exit /b 1
)

echo  [OK] Python found.
echo.
echo  Installing dependencies...
echo.

pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo  [ERROR] Installation failed. Check the output above.
    pause
    exit /b 1
)

echo.
echo  ==========================================
echo   Setup complete!
echo   Double-click run.bat to launch PromptForge.
echo  ==========================================
echo.
pause
