from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from bot.config import DATABASE_URL
from bot.models.database import Base
import logging

logger = logging.getLogger(__name__)


class Database:
    def __init__(self):
        self.engine = None
        self.async_session = None

    async def init(self):
        """Инициализация БД"""
        logger.info(f"🔧 Initializing database")
        logger.info(f"📍 Database URL: {DATABASE_URL}")

        try:
            self.engine = create_async_engine(DATABASE_URL, echo=False)
            self.async_session = sessionmaker(
                self.engine, class_=AsyncSession, expire_on_commit=False
            )

            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                
                # Автоматическая миграция telegram_id типа если это PostgreSQL
                if "postgresql" in DATABASE_URL.lower():
                    await self._fix_telegram_id_type(conn)

            logger.info("✅ Database initialized successfully")
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            raise

    async def _fix_telegram_id_type(self, conn):
        """Проверяет и исправляет тип колонки telegram_id с Integer на BigInteger"""
        try:
            # Проверяем текущий тип колонки
            result = await conn.execute(
                text("""
                    SELECT data_type FROM information_schema.columns 
                    WHERE table_name = 'users' AND column_name = 'telegram_id'
                """)
            )
            row = result.fetchone()
            
            if row and row[0] == "integer":
                logger.warning("⚠️  Detected Integer type for telegram_id, converting to BigInteger...")
                try:
                    await conn.execute(
                        text("""
                            ALTER TABLE users 
                            ALTER COLUMN telegram_id TYPE bigint USING telegram_id::bigint
                        """)
                    )
                    logger.info("✅ Successfully converted telegram_id to BigInteger")
                except Exception as e:
                    logger.warning(f"⚠️  Could not convert telegram_id type: {e}")
                    # Это не критическая ошибка, продолжаем работу
        except Exception as e:
            logger.debug(f"Could not check telegram_id type: {e}")

    async def close(self):
        """Закрытие БД"""
        if self.engine:
            await self.engine.dispose()

    def get_session(self):
        """Получить сессию"""
        return self.async_session()


db = Database()
