import asyncio
import logging
import subprocess
import os
from pathlib import Path
import ssl
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, MenuButtonWebApp, MenuButtonDefault, WebAppInfo
from aiogram.fsm.storage.memory import MemoryStorage
import threading

from bot.config import BOT_TOKEN
from bot.models.init_db import db
from bot.handlers import navigation, resell, statistics, rental
from bot.tasks.notifications import check_rental_notifications

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


async def set_menu_button(bot: Bot):
    """Установить Menu Button с Web App"""
    try:
        # Получаем URL приложения из переменных окружения или используем по умолчанию
        app_url = os.getenv('WEB_APP_URL', 'https://web-production-70ac2.up.railway.app')
        
        # Создаём Web App кнопку
        menu_button = MenuButtonWebApp(
            text="Helper",
            web_app=WebAppInfo(url=app_url)
        )
        
        # Устанавливаем её как Menu Button
        await bot.set_chat_menu_button(menu_button=menu_button)
        logger.info(f"✅ Menu Button установлен: {app_url}")
    except Exception as e:
        logger.error(f"❌ Ошибка при установке Menu Button: {e}")




async def set_default_app_button(bot: Bot):
    """Установить Default Web App Button (кнопка в превью)"""
    try:
        # Получаем URL приложения из переменных окружения или используем по умолчанию
        app_url = os.getenv('WEB_APP_URL', 'https://web-production-70ac2.up.railway.app')
        
        # Создаём Default Web App кнопку для превью
        # Это будет кнопка которая появляется ПЕРЕД входом в чат
        default_button = MenuButtonWebApp(
            text="Open App",
            web_app=WebAppInfo(url=app_url)
        )
        await bot.set_chat_menu_button(menu_button=default_button)
        logger.info(f"✅ Default Web App Button установлен: {app_url}")
    except Exception as e:
        logger.error(f"❌ Ошибка при установке Default Web App Button: {e}")

async def main():
    """Главная функция"""
    # Логируем информацию о конфигурации
    from bot.config import DATABASE_URL
    logger.info(f"🔍 Database configuration:")
    logger.info(f"   DATABASE_URL: {DATABASE_URL}")
    
    if "postgresql" in DATABASE_URL or "postgres" in DATABASE_URL:
        logger.info(f"   Using PostgreSQL (persistent database)")
        # Запускаем миграции для PostgreSQL
        logger.info("🔧 Running PostgreSQL migrations...")
        try:
            from migrate_postgresql import migrate_postgresql
            success = migrate_postgresql()
            if not success:
                logger.warning("⚠️ Migrations completed with warnings, but continuing...")
        except Exception as e:
            logger.warning(f"⚠️ Could not run migrations: {e}")
            import traceback
            logger.warning(traceback.format_exc())
    else:
        logger.info(f"   Using SQLite (local)")
    
    logger.info(f"   RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT', 'NOT SET')}")
    
    # Инициализируем БД
    await db.init()
    logger.info("✅ Database initialized")
    
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
    
    # Устанавливаем Menu Button
    await set_menu_button(bot)
    
    # Устанавливаем Default Web App Button
    await set_default_app_button(bot)
    
    # На production (Railway) используем HTTP без SSL
    # Railway автоматически добавляет HTTPS на уровне reverse proxy
    logger.info("🔧 Importing Flask web server...")
    try:
        from bot.web.app import run_web_server
        logger.info("✅ Flask web server imported successfully")
    except Exception as e:
        logger.error(f"❌ Failed to import Flask web server: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise
    
    port_str = os.getenv("PORT", "5000")
    port = int(port_str)  # Railway передаёт PORT в окружении
    is_production = os.getenv("RAILWAY_ENVIRONMENT") is not None
    
    logger.info(f"🌐 Web server configuration:")
    logger.info(f"   PORT from env: {port_str}")
    logger.info(f"   PORT as int: {port}")
    logger.info(f"   RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT', 'NOT SET')}")
    logger.info(f"   Is Production: {is_production}")
    
    if is_production:
        # На production: без SSL, Railway сам управляет HTTPS
        web_thread = threading.Thread(target=run_web_server, args=(port, None, None), daemon=True)
        logger.info("🟡 Production mode: Web server will use HTTP (Railway handles HTTPS)")
    else:
        # Локально: пытаемся использовать SSL если доступны сертификаты
        cert_file, key_file = ensure_ssl_certs()
        if cert_file and key_file:
            web_thread = threading.Thread(target=run_web_server, args=(port, cert_file, key_file), daemon=True)
            logger.info("🟢 Development mode: Web server will use HTTPS")
        else:
            web_thread = threading.Thread(target=run_web_server, args=(port, None, None), daemon=True)
            logger.info("🟡 Development mode: Web server will use HTTP")
    
    web_thread.start()
    logger.info(f"✅ Web server thread started on port {port}")
    
    # Даём серверу время на запуск и проверяем, жив ли поток
    import time
    time.sleep(2)
    if not web_thread.is_alive():
        logger.error("❌ Web server thread failed to start!")
        logger.error("Check logs above for Flask errors")
    else:
        logger.info(f"✅ Web server thread is alive and listening on 0.0.0.0:{port}")
    
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
