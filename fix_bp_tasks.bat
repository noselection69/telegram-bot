@echo off
REM Скрипт для быстрого исправления BP tasks на Railway

echo.
echo ========================================
echo BP TASKS FIX - QUICK RESET
echo ========================================
echo.
echo Этот скрипт вызовет admin endpoint чтобы
echo принудительно обновить все BP tasks на Railway
echo.

setlocal enabledelayedexpansion

echo Укажите URL вашего приложения на Railway:
echo Пример: https://gta5bot-prod.railway.app
echo.
set /p RAILWAY_URL="Введите URL (или Enter для пропуска): "

if "!RAILWAY_URL!"=="" (
    echo.
    echo ❌ Ошибка: URL не указан!
    echo.
    echo Используйте вместо этого:
    echo python fix_bp_tasks_now.py
    echo.
    pause
    exit /b 1
)

REM Убираем слеш в конце если есть
if "!RAILWAY_URL:~-1!"=="/" set "RAILWAY_URL=!RAILWAY_URL:~0,-1!"

REM Проверяем что URL содержит https://
if not "!RAILWAY_URL:https://=!" == "!RAILWAY_URL!" (
    echo ✅ URL содержит https
) else (
    set "RAILWAY_URL=https://!RAILWAY_URL!"
)

echo.
echo 🔄 Вызываю admin endpoint...
echo    URL: !RAILWAY_URL!/api/admin/reset-bp-tasks
echo.

python -c "^
import requests, json, sys; ^
try: ^
    resp = requests.post('!RAILWAY_URL!/api/admin/reset-bp-tasks', headers={'X-Admin-Key': 'gta5rp_admin_2024'}, timeout=30); ^
    print(f'Response: {resp.status_code}'); ^
    if resp.status_code == 200: ^
        print('✅ SUCCESS!'); ^
        data = resp.json(); ^
        print(f'Message: {data.get(\"message\")}'); ^
        print(f'Tasks added: {data.get(\"added\")}'); ^
    else: ^
        print(f'❌ ERROR: {resp.status_code}'); ^
        print(f'Response: {resp.text}'); ^
except Exception as e: ^
    print(f'❌ ERROR: {e}'); ^
"

echo.
echo ✅ Готово!
echo Проверьте веб-интерфейс чтобы убедиться что BP tasks обновились
echo.
pause
