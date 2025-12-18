#!/usr/bin/env python3
"""
Удаление всех BP заданий из базы данных на Railway
Используйте только если нужно очистить таблицу перед переинициализацией
"""
import os
import sys

DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    print("❌ DATABASE_URL не найден в переменных окружения")
    print("Локальная разработка - нечего удалять")
    sys.exit(0)

print("⚠️  ВНИМАНИЕ: Вы собираетесь удалить ВСЕ BP задания!")
print(f"DATABASE_URL: {DATABASE_URL[:50]}...")

try:
    from sqlalchemy import create_engine, text
    
    db_url = DATABASE_URL.replace("+asyncpg", "+psycopg2")
    if "postgresql://" in db_url and "+psycopg2" not in db_url:
        db_url = db_url.replace("postgresql://", "postgresql+psycopg2://")
    
    print("🔌 Подключаюсь к PostgreSQL...")
    engine = create_engine(db_url)
    conn = engine.connect()
    
    # Проверяем текущее количество
    result = conn.execute(text("SELECT COUNT(*) FROM bp_tasks")).scalar() or 0
    print(f"📊 Текущих заданий в bp_tasks: {result}")
    
    if result == 0:
        print("✅ Таблица уже пуста, нечего удалять")
        conn.close()
        sys.exit(0)
    
    # Удаляем все заданий
    print("🗑️  Удаляю все BP задания...")
    conn.execute(text("DELETE FROM bp_tasks"))
    conn.commit()
    
    # Проверяем результат
    result_after = conn.execute(text("SELECT COUNT(*) FROM bp_tasks")).scalar() or 0
    print(f"✅ После удаления: {result_after} заданий")
    
    if result_after == 0:
        print("✅ Таблица bp_tasks успешно очищена!")
    else:
        print(f"⚠️  Осталось {result_after} заданий, удаление может быть неполным")
    
    conn.close()
    sys.exit(0)
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
