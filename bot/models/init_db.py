from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from bot.config import DATABASE_URL
from bot.models.database import Base


class Database:
    def __init__(self):
        self.engine = None
        self.async_session = None
    
    async def init(self):
        """Инициализация БД"""
        self.engine = create_async_engine(DATABASE_URL, echo=False)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def close(self):
        """Закрытие БД"""
        if self.engine:
            await self.engine.dispose()
    
    def get_session(self):
        """Получить сессию"""
        return self.async_session()


db = Database()
