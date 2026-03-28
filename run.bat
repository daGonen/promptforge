@echo off
title PromptForge
cd /d "%~dp0"
python main.py
if errorlevel 1 (
    echo.
    echo  [ERROR] PromptForge failed to start.
    echo  Try running install.bat first.
    echo.
    pause
)
