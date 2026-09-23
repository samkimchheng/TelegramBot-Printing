@echo off
title Telegram Invitation Bot Server
cd /d "%~dp0"
echo ========================================================
echo   Telegram Invitation Printing & Order Bot Server
echo ========================================================
echo.

:loop
echo [%date% %time%] Starting Telegram Bot...
py bot.py
echo.
echo [%date% %time%] WARNING: Bot stopped or disconnected. Restarting in 5 seconds...
timeout /t 5
goto loop
