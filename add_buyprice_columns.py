"""
Миграция: добавление колонок item_id и sale_price в таблицу buy_prices
"""
import os
import sys

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from bot.config import DATABASE_URL

def migrate():
    """Добавляем колонки item_id и sale_price в buy_prices"""
    
    # Преобразуем URL для синхронного доступа
    sync_url = DATABASE_URL
    if "postgresql+asyncpg://" in sync_url:
        sync_url = sync_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    elif "postgresql://" in sync_url and "+psycopg2" not in sync_url:
        sync_url = sync_url.replace("postgresql://", "postgresql+psycopg2://")
    elif "sqlite+aiosqlite://" in sync_url:
        sync_url = sync_url.replace("sqlite+aiosqlite://", "sqlite://")
    
    print(f"🔧 Миграция buy_prices: подключение к БД...")
    
    if "sqlite" in sync_url:
        engine = create_engine(sync_url, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(sync_url)
    
    with engine.connect() as conn:
        # Проверяем, есть ли уже колонка item_id
        try:
            result = conn.execute(text("SELECT item_id FROM buy_prices LIMIT 1"))
            print("✅ Колонка item_id уже существует")
        except Exception:
            # Добавляем колонку item_id
            try:
                conn.execute(text("ALTER TABLE buy_prices ADD COLUMN item_id INTEGER REFERENCES items(id)"))
                conn.commit()
                print("✅ Колонка item_id добавлена")
            except Exception as e:
                print(f"⚠️ Ошибка добавления item_id: {e}")
        
        # Проверяем, есть ли уже колонка sale_price
        try:
            result = conn.execute(text("SELECT sale_price FROM buy_prices LIMIT 1"))
            print("✅ Колонка sale_price уже существует")
        except Exception:
            # Добавляем колонку sale_price
            try:
                conn.execute(text("ALTER TABLE buy_prices ADD COLUMN sale_price FLOAT"))
                conn.commit()
                print("✅ Колонка sale_price добавлена")
            except Exception as e:
                print(f"⚠️ Ошибка добавления sale_price: {e}")
        
        print("✅ Миграция buy_prices завершена!")

if __name__ == "__main__":
    migrate()
