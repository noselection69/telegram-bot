#!/usr/bin/env python3
"""
Скрипт для прямого применения миграций на PostgreSQL
Запустить перед деплоем на Railway
"""
import os
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Add bot to path
sys.path.insert(0, str(Path(__file__).parent))

from bot.config import DATABASE_URL
from sqlalchemy import create_engine, text

def migrate_postgresql():
    """Применяет необходимые миграции к PostgreSQL БД"""
    
    if "postgresql" not in DATABASE_URL and "postgres" not in DATABASE_URL:
        logger.error("❌ Это не PostgreSQL база данных!")
        return False
    
    try:
        logger.info("🔗 Подключаемся к PostgreSQL...")
        
        # Конвертируем async DATABASE_URL в sync (postgresql+asyncpg -> postgresql+psycopg2)
        sync_db_url = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
        if sync_db_url == DATABASE_URL:
            # На случай если уже sync URL
            sync_db_url = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://")
        
        logger.info(f"📝 Используем sync URL для миграции")
        engine = create_engine(sync_db_url, echo=False)
        
        with engine.connect() as connection:
            # 1. Добавляем has_platinum_vip колонку
            logger.info("🔧 Проверяем has_platinum_vip колонку...")
            result = connection.execute(
                text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name='users' AND column_name='has_platinum_vip'
                );
                """)
            )
            
            if not result.scalar():
                logger.info("➕ Добавляем has_platinum_vip колонку в users...")
                connection.execute(
                    text("ALTER TABLE users ADD COLUMN has_platinum_vip BOOLEAN DEFAULT false;")
                )
                connection.commit()
                logger.info("✅ has_platinum_vip добавлена")
            else:
                logger.info("✅ has_platinum_vip уже существует")
            
            # 2. Добавляем is_past колонку
            logger.info("🔧 Проверяем is_past колонку...")
            result = connection.execute(
                text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name='rentals' AND column_name='is_past'
                );
                """)
            )
            
            if not result.scalar():
                logger.info("➕ Добавляем is_past колонку в rentals...")
                connection.execute(
                    text("ALTER TABLE rentals ADD COLUMN is_past BOOLEAN DEFAULT false;")
                )
                connection.commit()
                logger.info("✅ is_past добавлена")
            else:
                logger.info("✅ is_past уже существует")
            
            # 3. Проверяем BPTask таблицу
            logger.info("🔧 Проверяем BPTask таблицу...")
            result = connection.execute(
                text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name='bp_tasks'
                );
                """)
            )
            
            if result.scalar():
                logger.info("✅ BPTask таблица существует")
            else:
                logger.info("⚠️ BPTask таблица не найдена (она будет создана автоматически)")
            
            # 4. Проверяем BPCompletion таблицу
            logger.info("🔧 Проверяем BPCompletion таблицу...")
            result = connection.execute(
                text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name='bp_completions'
                );
                """)
            )
            
            if result.scalar():
                logger.info("✅ BPCompletion таблица существует")
            else:
                logger.info("⚠️ BPCompletion таблица не найдена (она будет создана автоматически)")
        
        logger.info("\n✅ Миграция завершена успешно!")
        engine.dispose()
        return True
        
    except Exception as e:
        logger.error(f"\n❌ Ошибка миграции: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = migrate_postgresql()
    sys.exit(0 if success else 1)
