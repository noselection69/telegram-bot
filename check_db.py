#!/usr/bin/env python3
"""Проверка структуры БД в Railway"""
import os
import sys
from sqlalchemy import create_engine, text, inspect

# Получаем DATABASE_URL из .env
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    # Пробуем default для локальной разработки
    DATABASE_URL = 'sqlite:///bot_data.db'

print(f"📊 Checking database: {DATABASE_URL[:50]}...")

try:
    # Используем правильный драйвер
    if "postgresql" in DATABASE_URL or "postgres" in DATABASE_URL:
        SYNC_DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg", "postgresql+psycopg2")
        SYNC_DATABASE_URL = SYNC_DATABASE_URL.replace("postgresql+asyncpg", "postgresql")
        print(f"✅ Using PostgreSQL")
        connect_args = {}
    else:
        SYNC_DATABASE_URL = DATABASE_URL.replace("sqlite+aiosqlite", "sqlite")
        print(f"✅ Using SQLite")
        connect_args = {"check_same_thread": False}
    
    engine = create_engine(SYNC_DATABASE_URL, connect_args=connect_args)
    
    # Проверяем таблицы
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"\n📋 Tables: {tables}")
    
    # Проверяем структуру таблицы rentals
    if 'rentals' in tables:
        columns = inspector.get_columns('rentals')
        print(f"\n📊 Rentals table columns:")
        for col in columns:
            print(f"   - {col['name']}: {col['type']}")
        
        # Проверяем наличие is_past
        has_is_past = any(col['name'] == 'is_past' for col in columns)
        print(f"\n🔍 Column 'is_past' exists: {has_is_past}")
    
    # Проверяем данные
    with engine.connect() as conn:
        # Проверяем количество записей в rentals
        result = conn.execute(text("SELECT COUNT(*) as count FROM rentals"))
        count = result.scalar()
        print(f"\n📈 Rentals count: {count}")
        
        # Показываем последние 3 записи
        result = conn.execute(text("""
            SELECT id, user_id, car_id, rental_start, rental_end, is_past 
            FROM rentals 
            ORDER BY id DESC 
            LIMIT 3
        """))
        print(f"\n📝 Last 3 rentals:")
        for row in result:
            print(f"   ID={row[0]}, user_id={row[1]}, car_id={row[2]}, start={row[3]}, end={row[4]}, is_past={row[5]}")
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
