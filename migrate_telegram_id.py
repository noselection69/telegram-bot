#!/usr/bin/env python3
"""
Миграционный скрипт для обновления типа telegram_id с Integer на BigInteger
в существующей базе данных PostgreSQL на Railway.

Использование:
    python migrate_telegram_id.py
"""

import asyncio
import os
import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def migrate():
    """Выполнить миграцию telegram_id"""
    # Получаем DATABASE_URL из переменной окружения
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        logger.error("❌ DATABASE_URL не установлена!")
        return False
    
    # Преобразуем postgresql:// в postgresql+asyncpg://
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
    elif database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+asyncpg://")
    
    logger.info(f"📍 Подключение к базе данных...")
    
    try:
        engine = create_async_engine(database_url, echo=False)
        
        async with engine.begin() as conn:
            # Проверяем текущий тип колонки
            logger.info("🔍 Проверяем текущий тип колонки telegram_id...")
            result = await conn.execute(
                text("""
                    SELECT data_type FROM information_schema.columns 
                    WHERE table_name = 'users' AND column_name = 'telegram_id'
                """)
            )
            row = result.fetchone()
            
            if row:
                current_type = row[0]
                logger.info(f"   Текущий тип: {current_type}")
                
                if current_type == "bigint":
                    logger.info("✅ Колонка уже имеет тип BigInteger (bigint), миграция не требуется")
                    return True
                
                logger.info("⚠️  Начинаем миграцию Integer → BigInteger...")
                
                # Для PostgreSQL выполняем ALTER TABLE
                await conn.execute(
                    text("""
                        ALTER TABLE users 
                        ALTER COLUMN telegram_id TYPE bigint USING telegram_id::bigint
                    """)
                )
                
                logger.info("✅ Миграция успешно выполнена!")
                logger.info("   Колонка telegram_id обновлена на тип BigInteger")
                return True
            else:
                logger.error("❌ Таблица users или колонка telegram_id не найдена")
                return False
                
    except Exception as e:
        logger.error(f"❌ Ошибка при миграции: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await engine.dispose()


if __name__ == "__main__":
    success = asyncio.run(migrate())
    exit(0 if success else 1)
