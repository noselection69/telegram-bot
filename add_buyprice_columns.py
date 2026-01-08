"""
Миграция: добавление колонок item_id и sale_price в таблицу buy_prices
"""
import os
import sys

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from bot.models.database import engine

def migrate():
    """Добавляем колонки item_id и sale_price в buy_prices"""
    
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
        
        print("\n✅ Миграция завершена!")

if __name__ == "__main__":
    migrate()
