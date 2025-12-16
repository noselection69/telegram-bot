#!/usr/bin/env python3
"""
Скрипт для подготовки проекта к деплою
Автоматически настраивает все необходимое
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Запустить команду с описанием"""
    print(f"\n📍 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Ошибка: {result.stderr}")
            return False
        print(f"✅ {description} - успешно")
        return True
    except Exception as e:
        print(f"❌ Ошибка при выполнении: {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 Подготовка проекта к деплою на Railway/Render")
    print("=" * 60)
    
    # Проверка файлов
    files_to_check = [
        'requirements.txt',
        'Procfile',
        'railway.toml',
        '.gitignore',
        '.env',
        'bot/main.py',
        'bot/web/app.py'
    ]
    
    print("\n📋 Проверка необходимых файлов...")
    for file in files_to_check:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ⚠️  {file} - не найден")
    
    # Инициализация Git
    if not os.path.exists('.git'):
        run_command('git init', 'Инициализация Git репозитория')
    else:
        print("✅ Git репозиторий уже инициализирован")
    
    # Добавление файлов
    run_command('git add .', 'Добавление файлов в Git')
    
    # Коммит
    run_command('git commit -m "Initial commit: Telegram bot ready for deployment"', 'Создание коммита')
    
    print("\n" + "=" * 60)
    print("🎉 Проект готов к деплою!")
    print("=" * 60)
    
    print("\n📖 Следующие шаги:")
    print("1. Перейди на https://railway.app")
    print("2. Нажми 'Start Project' → 'Deploy from GitHub'")
    print("3. Авторизуйся и выбери свой репозиторий")
    print("4. Добавь переменные окружения (BOT_TOKEN, DATABASE_URL и т.д.)")
    print("5. Деплой начнется автоматически!")
    
    print("\n💡 Для локального тестирования перед деплоем:")
    print("   python -m bot.main")
    
    print("\n📚 Подробная инструкция в: DEPLOY.md")

if __name__ == '__main__':
    main()
