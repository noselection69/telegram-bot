#!/usr/bin/env python3
"""Безопасное обновление main.py"""

# Читаем файл
with open('bot/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Добавляем MenuButtonDefault в импорты (строка 9)
content = content.replace(
    'from aiogram.types import BotCommand, MenuButtonWebApp, WebAppInfo',
    'from aiogram.types import BotCommand, MenuButtonWebApp, MenuButtonDefault, WebAppInfo'
)

# 2. Обновляем текст кнопки с "📱 Открыть приложение" на "Helper"
content = content.replace(
    'text="📱 Открыть приложение",',
    'text="Helper",'
)

# 3. Добавляем функцию set_default_app_button после set_menu_button
# Ищем конец функции set_menu_button
marker = '''async def set_menu_button(bot: Bot):
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
        logger.error(f"❌ Ошибка при установке Menu Button: {e}")'''

new_function = '''

async def set_default_app_button(bot: Bot):
    """Установить Default Web App Button (кнопка в превью)"""
    try:
        default_button = MenuButtonDefault()
        await bot.set_chat_menu_button(menu_button=default_button)
        logger.info("✅ Default Web App Button установлен")
    except Exception as e:
        logger.error(f"❌ Ошибка при установке Default Web App Button: {e}")'''

if 'async def set_default_app_button' not in content:
    content = content.replace(marker, marker + new_function)

# 4. Добавляем вызов функции в main() после await set_menu_button(bot)
content = content.replace(
    '    # Устанавливаем Menu Button\n    await set_menu_button(bot)\n    ',
    '    # Устанавливаем Menu Button\n    await set_menu_button(bot)\n    \n    # Устанавливаем Default Web App Button\n    await set_default_app_button(bot)\n    '
)

# Пишем файл
with open('bot/main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ bot/main.py обновлён успешно!")
