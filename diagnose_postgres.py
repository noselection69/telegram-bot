#!/usr/bin/env python3
"""
Диагностика подключения к PostgreSQL на Railway
"""
import os
import sys
from sqlalchemy import create_engine, text, inspect

print("🔍 PostgreSQL Connection Diagnostics")
print("=" * 80)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("\n❌ ERROR: DATABASE_URL environment variable not set!")
    print("\nTo set it manually:")
    print("  export DATABASE_URL='postgresql+psycopg2://user:pass@host:port/db'")
    print("\nOr on Railway, add in .env or in Railway Dashboard")
    sys.exit(1)

print(f"\n📍 DATABASE_URL found")
print(f"   Host/DB: {DATABASE_URL.split('@')[-1][:50]}...")

# Конвертируем asyncpg URL в psycopg2
SYNC_DATABASE_URL = DATABASE_URL
if "postgresql+asyncpg" in DATABASE_URL:
    print("   Converting asyncpg → psycopg2...")
    SYNC_DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg", "postgresql+psycopg2")

# Пытаемся подключиться
print("\n🔗 Attempting connection...")
try:
    engine = create_engine(SYNC_DATABASE_URL, echo=False, pool_pre_ping=True)
    
    # Базовый тест подключения
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("   ✅ Connection successful!")
        
        # Проверяем версию PostgreSQL
        result = conn.execute(text("SELECT version()"))
        version = result.scalar()
        print(f"   📋 PostgreSQL: {version[:60]}...")
        
        # Получаем текущую БД
        result = conn.execute(text("SELECT current_database()"))
        db_name = result.scalar()
        print(f"   📁 Database: {db_name}")
        
        # Получаем текущего пользователя
        result = conn.execute(text("SELECT current_user"))
        user = result.scalar()
        print(f"   👤 User: {user}")
        
except Exception as e:
    print(f"   ❌ Connection failed: {e}")
    sys.exit(1)

# Проверяем таблицы
print("\n📊 Tables in database:")
try:
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if not tables:
        print("   ❌ No tables found! Database might be empty.")
    else:
        for table in sorted(tables):
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
            print(f"   - {table}: {count} rows")
    
    # Специально проверяем bp_tasks
    print("\n🎯 Checking bp_tasks table:")
    if "bp_tasks" not in tables:
        print("   ❌ Table 'bp_tasks' DOES NOT EXIST!")
        print("   → Need to run migrations: python migrate_postgresql.py")
    else:
        print("   ✅ Table 'bp_tasks' exists")
        
        # Детали таблицы
        cols = inspector.get_columns("bp_tasks")
        print("      Columns:")
        for col in cols:
            print(f"        - {col['name']}: {col['type']}")
        
        # Считаем BP задания
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM bp_tasks"))
            count = result.scalar()
            print(f"      Total BP tasks: {count}")
            
            if count > 0:
                # Группируем по категориям
                result = conn.execute(text("""
                    SELECT category, COUNT(*) as cnt 
                    FROM bp_tasks 
                    GROUP BY category 
                    ORDER BY category
                """))
                print("      By category:")
                for row in result:
                    cat, cnt = row
                    print(f"        - {cat}: {cnt}")
            else:
                print("      ⚠️  No BP tasks in database! Need to initialize.")

except Exception as e:
    print(f"   ❌ Error checking tables: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("✅ Diagnostics completed!")
