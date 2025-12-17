import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Bot token from Telegram BotFather
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Database configuration
BASE_DIR = Path(__file__).parent.parent

# Проверяем, доступна ли PostgreSQL на Railway
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # На Railway: используем PostgreSQL из переменной окружения
    print(f"✅ Using PostgreSQL database from DATABASE_URL")
    print(f"   RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT', 'NOT SET')}")
    
    # Преобразуем postgresql:// в postgresql+psycopg2:// для SQLAlchemy async
    if DATABASE_URL.startswith("postgresql://"):
        ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    elif DATABASE_URL.startswith("postgres://"):
        ASYNC_DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://")
    else:
        ASYNC_DATABASE_URL = DATABASE_URL
    
    print(f"   ASYNC_DATABASE_URL configured for async operations")
    DATABASE_URL = ASYNC_DATABASE_URL
    
else:
    # Локально: используем SQLite
    print(f"📍 DATABASE_URL not set, using SQLite locally")
    DATA_DIR = BASE_DIR
    DB_PATH = DATA_DIR / "bot_data.db"
    print(f"   Database path: {DB_PATH}")
    DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

# Timezone
TIMEZONE = "Europe/Moscow"