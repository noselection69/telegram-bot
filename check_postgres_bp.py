#!/usr/bin/env python3
"""
Проверяем BP tasks на PostgreSQL в Railway
"""
import os
import sys
from sqlalchemy import create_engine, text, inspect

# Подставляем правильный DATABASE_URL из Railway
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL not set! Setting to SQLite for local testing...")
    DATABASE_URL = "sqlite:///bot_data.db"
    from bot.models.database import Base
    engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
else:
    print(f"📍 Found DATABASE_URL: {DATABASE_URL[:50]}...")
    # Конвертируем asyncpg URL в psycopg2 для синхронной работы
    if "postgresql+asyncpg" in DATABASE_URL:
        print("   Converting asyncpg → psycopg2 for sync access...")
        DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg", "postgresql+psycopg2")
    
    from bot.models.database import Base
    engine = create_engine(DATABASE_URL, echo=False)

print(f"\n🔍 Checking BP tasks in database: {DATABASE_URL[:60]}...")
print("=" * 80)

try:
    with engine.connect() as conn:
        # 1. Проверяем существует ли таблица bp_task
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"\n📋 Available tables: {tables}")
        
        # Проверяем есть ли таблица с правильным названием
        bp_table = None
        for t in tables:
            if "bp_task" in t.lower():
                bp_table = t
                break
        
        if not bp_table:
            print(f"\n❌ ERROR: bp_task table does not exist! Found tables: {tables}")
            sys.exit(1)
        
        print(f"✅ Found table: {bp_table}")
        
        # 2. Проверяем schema таблицы
        print(f"\n📝 Table '{bp_table}' schema:")
        columns = inspector.get_columns(bp_table)
        for col in columns:
            print(f"   - {col['name']}: {col['type']} (nullable: {col['nullable']})")
        
        # 3. Считаем количество заданий
        result = conn.execute(text(f"SELECT COUNT(*) FROM {bp_table}"))
        total_count = result.scalar()
        print(f"\n📊 Total BP tasks: {total_count}")
        
        # 4. Группируем по категориям
        result = conn.execute(text(f"""
            SELECT category, COUNT(*) as cnt 
            FROM {bp_table} 
            GROUP BY category 
            ORDER BY category
        """))
        
        print("\n📂 Tasks by category:")
        for row in result:
            category, count = row
            print(f"   {category}: {count}")
        
        # 5. Показываем первые 10 заданий
        result = conn.execute(text(f"""
            SELECT id, name, category, bp_without_vip, bp_with_vip 
            FROM {bp_table} 
            LIMIT 10
        """))
        
        print("\n📋 Sample tasks (first 10):")
        for row in result:
            task_id, name, category, bp_no_vip, bp_vip = row
            print(f"   [{task_id}] {name[:60]}... ({category}): {bp_no_vip}→{bp_vip} BP")
        
        # 6. Проверяем есть ли задания для RP миссий
        result = conn.execute(text(f"""
            SELECT COUNT(*) FROM {bp_table} 
            WHERE name LIKE '%ферм%' OR name LIKE '%мусор%' OR name LIKE '%фарм%'
        """))
        farm_count = result.scalar()
        print(f"\n🌾 Farm-related tasks: {farm_count}")
        
        # 7. Проверяем старые задания (если существуют)
        result = conn.execute(text(f"""
            SELECT id, name FROM {bp_table} 
            WHERE name IN ('Farm', 'Mine', 'Build', 'Port', 'Casino')
            LIMIT 5
        """))
        old_tasks = result.fetchall()
        if old_tasks:
            print(f"\n⚠️  Found OLD placeholder tasks (should be deleted):")
            for task in old_tasks:
                print(f"   [{task[0]}] {task[1]}")

except Exception as e:
    print(f"\n❌ ERROR connecting to database: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✅ Check completed!")
