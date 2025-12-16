import asyncio
import logging
import subprocess
import os
from pathlib import Path
import ssl
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
import threading

from bot.config import BOT_TOKEN
from bot.models.init_db import db
from bot.handlers import navigation, resell, statistics, rental
from bot.tasks.notifications import check_rental_notifications

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def set_bot_commands(bot: Bot):
    """Установить команды бота"""
    commands = [
        BotCommand(command="start", description="Начать работу"),
        BotCommand(command="menu", description="Главное меню"),
    ]
    await bot.set_my_commands(commands)


async def main():
    """Главная функция"""
    # Определяем режим запуска
    run_mode = os.getenv("RUN_MODE", "bot")  # "web" или "bot"
    logger.info(f"🚀 RUN_MODE: {run_mode}")
    
    # Если режим web - ничего не запускаем
    # Flask будет запущен gunicorn'ом из bot.web.app
    if run_mode == "web":
        logger.info("🌐 Web mode detected - Flask will be managed by gunicorn")
        logger.info("ℹ️  To run bot polling, set RUN_MODE=bot or start a separate worker")
        # Просто ждём, чтобы процесс не завершился
        try:
            while True:
                await asyncio.sleep(60)
        except KeyboardInterrupt:
            logger.info("Process interrupted")
        return
    
    # Режим bot - запускаем бота и его компоненты
    logger.info("🤖 Bot mode detected - starting bot polling")
    
    # Инициализируем БД
    await db.init()
    logger.info("Database initialized")
    
    # Создаем бот и диспетчер
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Регистрируем роутеры
    dp.include_router(navigation.router)
    dp.include_router(resell.router)
    dp.include_router(statistics.router)
    dp.include_router(rental.router)
    
    # Устанавливаем команды
    await set_bot_commands(bot)
    logger.info("Bot commands set")
    
    # Запускаем фоновую задачу уведомлений
    notification_task = asyncio.create_task(check_rental_notifications(bot))
    
    # Запускаем polling
    try:
        logger.info("Starting bot polling...")
        await dp.start_polling(bot)
    finally:
        notification_task.cancel()
        await bot.session.close()
        await db.close()
        logger.info("Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())
