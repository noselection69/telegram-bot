#!/bin/bash
# Скрипт для запуска миграции PostgreSQL на Railway
# Установить переменную DATABASE_URL и запустить

if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL не установлена!"
    exit 1
fi

python migrate_postgresql.py
