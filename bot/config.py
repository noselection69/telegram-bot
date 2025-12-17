import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Bot token from Telegram BotFather
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Database
BASE_DIR = Path(__file__).parent.parent

# Используем постоянное хранилище на Railway если доступно, иначе локальную папку
if os.getenv("RAILWAY_ENVIRONMENT"):
    # На Railway: сохраняем в /app/data (постоянное Volume)
    # Railway Volume монтируется как /app/data - это PERSISTENT storage
    DATA_DIR = Path("/app/data")
    try:
        DATA_DIR.mkdir(exist_ok=True, parents=True)
        print(f"✅ Using Railway Volume for data: {DATA_DIR}")
        print(f"   RAILWAY_ENVIRONMENT={os.getenv('RAILWAY_ENVIRONMENT')}")
        print(f"   RAILWAY_VOLUME_MOUNT_PATH={os.getenv('RAILWAY_VOLUME_MOUNT_PATH', 'NOT SET')}")
    except Exception as e:
        print(f"⚠️ Warning: Could not create data directory: {e}")
        # Fallback to project root if volume fails
        DATA_DIR = BASE_DIR
        print(f"📍 Falling back to project root: {DATA_DIR}")
else:
    # Локально: сохраняем в корень проекта
    DATA_DIR = BASE_DIR
    print(f"📍 Using local directory for data: {DATA_DIR}")

DB_PATH = DATA_DIR / "bot_data.db"
print(f"📊 Database path: {DB_PATH}")
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

# Timezone
TIMEZONE = "Europe/Moscow"
