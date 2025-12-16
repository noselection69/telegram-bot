@echo off
REM Start script for Telegram Bot on Windows

echo Starting Telegram Finance Bot...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install/update requirements
echo Installing dependencies...
pip install -q -r requirements.txt

REM Check if .env file exists
if not exist ".env" (
    echo.
    echo WARNING: .env file not found!
    echo Please create .env file from .env.example with your BOT_TOKEN
    echo.
    pause
    exit /b 1
)

REM Start the bot
echo.
echo =====================================
echo Starting bot...
echo =====================================
echo.
python -m bot.main

pause
