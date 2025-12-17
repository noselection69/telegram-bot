from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
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

            logger.info("✅ Database initialized successfully")
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            raise

    async def close(self):
        """Закрытие БД"""
        if self.engine:
            await self.engine.dispose()

    def get_session(self):
        """Получить сессию"""
        return self.async_session()


db = Database()
