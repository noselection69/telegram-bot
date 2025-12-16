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
    DATA_DIR = Path("/app/data")
    DATA_DIR.mkdir(exist_ok=True, parents=True)
else:
    # Локально: сохраняем в корень проекта
    DATA_DIR = BASE_DIR

DB_PATH = DATA_DIR / "bot_data.db"
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

# Timezone
TIMEZONE = "Europe/Moscow"
