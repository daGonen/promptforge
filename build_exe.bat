@echo off
title PromptForge — Build EXE
echo.
echo  Building PromptForge.exe with PyInstaller...
echo.

pip install pyinstaller >nul 2>&1

pyinstaller ^
  --noconfirm ^
  --onefile ^
  --windowed ^
  --name "PromptForge" ^
  --add-data "data;data" ^
  --add-data "core;core" ^
  --add-data "ui;ui" ^
  --add-data "config.py;." ^
  main.py

echo.
if exist dist\PromptForge.exe (
    echo  [OK] Build complete.
    echo  Your .exe is at: dist\PromptForge.exe
) else (
    echo  [ERROR] Build failed. Check output above.
)
echo.
pause
