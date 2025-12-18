#!/usr/bin/env python3
"""
Диагностика BP заданий - проверить БД локально и на Railway
"""
import os
import sys
from sqlalchemy import create_engine, text

def check_database(db_url, db_name="local"):
    """Проверить содержимое таблицы bp_tasks"""
    try:
        # Преобразуем URL для синхронного доступа
        sync_url = db_url
        if "+asyncpg" in sync_url:
            sync_url = sync_url.replace("+asyncpg", "+psycopg2")
        elif "postgresql://" in sync_url and "+psycopg2" not in sync_url:
            sync_url = sync_url.replace("postgresql://", "postgresql+psycopg2://")
        elif "sqlite+aiosqlite" in sync_url:
            sync_url = sync_url.replace("sqlite+aiosqlite://", "sqlite:///")
        
        print(f"\n🔍 Проверка БД [{db_name}]...")
        print(f"   URL: {sync_url[:60]}...")
        
        engine = create_engine(sync_url, echo=False)
        
        with engine.connect() as conn:
            # Получаем количество
            result = conn.execute(text("SELECT COUNT(*) FROM bp_tasks;"))
            count = result.scalar()
            print(f"   📊 Всего заданий: {count}")
            
            if count == 0:
                print(f"   ⚠️  Таблица пуста!")
                return False
            
            # Получаем категории и их количество
            result = conn.execute(text("""
                SELECT category, COUNT(*) as cnt FROM bp_tasks 
                GROUP BY category ORDER BY category;
            """))
            
            categories = {}
            for row in result.fetchall():
                cat, cnt = row
                categories[cat] = cnt
                print(f"   {cat}: {cnt}")
            
            # Проверяем нужные категории
            expected = {"Легкие": 28, "Средние": 19, "Тяжелые": 12}
            all_correct = True
            
            for cat, expected_count in expected.items():
                actual = categories.get(cat, 0)
                if actual != expected_count:
                    print(f"   ❌ {cat}: ожидается {expected_count}, получено {actual}")
                    all_correct = False
            
            if all_correct and count == 59:
                print(f"   ✅ Все правильно!")
                return True
            else:
                print(f"   ❌ Не совпадает!")
                return False
                
    except Exception as e:
        print(f"   ❌ Ошибка подключения: {e}")
        return False

# Локальная БД
try:
    from bot.config import DATABASE_URL
    check_database(DATABASE_URL, "LOCAL SQLite")
except:
    print("❌ Не удалось подключиться к локальной БД")

# Railway БД
railway_url = os.environ.get('DATABASE_URL')
if railway_url:
    check_database(railway_url, "RAILWAY PostgreSQL")
else:
    print("\n⚠️  DATABASE_URL для Railway не установлена")
    print("   Используйте: railway run python diagnostic_bp.py")
