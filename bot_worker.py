"""
Bot-only entry point (для worker процесса)
Запускает только aiogram бота БЕЗ Flask сервера
"""

import asyncio
import logging
from bot.main import main

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
