@echo off
REM Скрипт для подготовки проекта к деплою на Windows

echo.
echo ========================================
echo   Railway Deployment Preparation
echo ========================================
echo.

REM Проверка Git
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Git not found. Please install Git.
    pause
    exit /b 1
)

REM Инициализация Git
if not exist .git (
    echo Initializing Git repository...
    call git init
    call git branch -M main
    echo.
)

REM Добавление файлов
echo Adding files to Git...
call git add .

REM Коммит
echo Creating commit...
call git commit -m "Deploy: Bot ready for production"

echo.
echo ======================================
echo   Project is ready for deployment!
echo ======================================
echo.
echo Next steps:
echo   1. Go to https://railway.app
echo   2. Click "Start Project"
echo   3. Select "Deploy from GitHub"
echo   4. Connect your repository
echo   5. Add environment variables (BOT_TOKEN, etc.)
echo.
echo Or test locally:
echo   python -m bot.main
echo.
pause
