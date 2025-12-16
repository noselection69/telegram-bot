import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Bot token from Telegram BotFather
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Database
BASE_DIR = Path(__file__).parent.parent

# Используем постоянное хранилище на Railway если доступно, иначе локальную папку
is_production = os.getenv("RAILWAY_ENVIRONMENT") is not None

if is_production:
    # На Railway: сохраняем в /app/data (постоянное Volume)
    DATA_DIR = Path("/app/data")
    try:
        DATA_DIR.mkdir(exist_ok=True, parents=True)
        print(f"✅ Database directory created: {DATA_DIR}")
    except Exception as e:
        print(f"⚠️ Could not create data directory: {e}")
        DATA_DIR = BASE_DIR
else:
    # Локально: сохраняем в корень проекта
    DATA_DIR = BASE_DIR

DB_PATH = DATA_DIR / "bot_data.db"
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

print(f"📊 Database path: {DB_PATH}")
print(f"🌍 Environment: {'Production (Railway)' if is_production else 'Development (Local)'}")

# Timezone
TIMEZONE = "Europe/Moscow"
