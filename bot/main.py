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
from bot.web.app import run_web_server

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def ensure_ssl_certs():
    """Убедиться что SSL сертификаты существуют"""
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
    except ImportError:
        logger.warning("⚠️  cryptography не установлен. Web App использует HTTP.")
        return None, None
    
    certs_dir = Path("certs")
    certs_dir.mkdir(exist_ok=True)
    
    cert_file = certs_dir / "cert.pem"
    key_file = certs_dir / "key.pem"
    
    # Если сертификаты есть, используем их
    if cert_file.exists() and key_file.exists():
        logger.info("✅ SSL сертификаты найдены")
        return str(cert_file), str(key_file)
    
    # Генерируем новые сертификаты
    logger.info("🔐 Генерирую самоподписанные SSL сертификаты...")
    
    try:
        # Генерируем приватный ключ
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Генерируем сертификат
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName(u"localhost"),
                x509.DNSName(u"127.0.0.1"),
            ]),
            critical=False,
        ).sign(key, hashes.SHA256())
        
        # Сохраняем сертификат
        with open(cert_file, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        # Сохраняем ключ
        with open(key_file, "wb") as f:
            f.write(key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        logger.info(f"✅ SSL сертификаты созданы в {certs_dir}")
        return str(cert_file), str(key_file)
        
    except Exception as e:
        logger.error(f"❌ Ошибка при создании сертификатов: {e}")
        return None, None


async def set_bot_commands(bot: Bot):
    """Установить команды бота"""
    commands = [
        BotCommand(command="start", description="Начать работу"),
        BotCommand(command="menu", description="Главное меню"),
    ]
    await bot.set_my_commands(commands)


async def main():
    """Главная функция"""
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
    
    # Проверяем, запущены ли мы через gunicorn
    # Если да - Flask уже запущен, не нужно запускать в отдельном потоке
    is_gunicorn = "gunicorn" in os.environ.get("SERVER_SOFTWARE", "")
    is_worker_only = os.getenv("RAILWAY_SERVICE") == "worker" or os.getenv("WORKER_ONLY") == "true"
    
    if not is_gunicorn and not is_worker_only:
        # Генерируем SSL сертификаты
        cert_file, key_file = ensure_ssl_certs()
        
        # Запускаем веб-сервер в отдельном потоке с HTTPS (только для локальной разработки)
        if cert_file and key_file:
            web_thread = threading.Thread(target=run_web_server, args=(5000, cert_file, key_file), daemon=True)
            logger.info("🟢 Web server will use HTTPS")
        else:
            web_thread = threading.Thread(target=run_web_server, args=(5000, None, None), daemon=True)
            logger.info("🟡 Web server will use HTTP (Web App buttons disabled)")
        
        web_thread.start()
        logger.info("✅ Web server started on port 5000")
    else:
        if is_gunicorn:
            logger.info("⏭️  Skipping web server (Flask is managed by gunicorn)")
        else:
            logger.info("⏭️  Skipping web server (running as worker only)")
    
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
