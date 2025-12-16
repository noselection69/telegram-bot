import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Bot token from Telegram BotFather
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Database
BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "bot_data.db"
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

# Timezone
TIMEZONE = "Europe/Moscow"
