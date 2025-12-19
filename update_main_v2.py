#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Безопасное обновление main.py - v2"""
import re

# Читаем файл с явной кодировкой UTF-8
with open('bot/main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Ищем и обновляем импорты (строка с "from aiogram.types")
for i, line in enumerate(lines):
    if 'from aiogram.types import BotCommand, MenuButtonWebApp, WebAppInfo' in line:
        lines[i] = line.replace(
            'MenuButtonWebApp, WebAppInfo',
            'MenuButtonWebApp, MenuButtonDefault, WebAppInfo'
        )
        print(f"✅ Обновлен импорт на строке {i+1}")
        break

# Ищем set_menu_button и обновляем текст
for i, line in enumerate(lines):
    if 'text="' in line and 'Открыть приложение' in line:
        lines[i] = '            text="Helper",\n'
        print(f"✅ Обновлён текст кнопки на строке {i+1}")
        break

# Ищем конец функции set_menu_button и добавляем новую функцию
for i, line in enumerate(lines):
    if line.strip().startswith('async def set_menu_button'):
        # Ищем конец этой функции (следующая строка "async def" или "async def main")
        j = i + 1
        while j < len(lines):
            if j > i and lines[j].startswith('async def '):
                # Нашли начало следующей функции
                # Вставляем перед ней новую функцию
                new_func = '''

async def set_default_app_button(bot: Bot):
    """Установить Default Web App Button (кнопка в превью)"""
    try:
        default_button = MenuButtonDefault()
        await bot.set_chat_menu_button(menu_button=default_button)
        logger.info("✅ Default Web App Button установлен")
    except Exception as e:
        logger.error(f"❌ Ошибка при установке Default Web App Button: {e}")

'''
                if 'async def set_default_app_button' not in ''.join(lines):
                    lines.insert(j, new_func)
                    print(f"✅ Добавлена функция set_default_app_button перед строкой {j+1}")
                break
            j += 1
        break

# Ищем где вызывается set_menu_button и добавляем вызов set_default_app_button
for i, line in enumerate(lines):
    if 'await set_menu_button(bot)' in line:
        # Смотрим следующие строки
        if i + 1 < len(lines):
            next_line = lines[i + 1]
            # Если следующая строка не пустая и не является комментарием для следующего вызова
            if next_line.strip() and 'await set_default_app_button' not in next_line:
                # Вставляем новый вызов
                indent = len(line) - len(line.lstrip())
                new_call = ' ' * indent + '# Устанавливаем Default Web App Button\n'
                new_call += ' ' * indent + 'await set_default_app_button(bot)\n'
                new_call += '\n'
                lines.insert(i + 1, new_call)
                print(f"✅ Добавлен вызов set_default_app_button на строке {i+2}")
        break

# Пишем файл
with open('bot/main.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✅ bot/main.py обновлён успешно!")

# Проверяем синтаксис
import py_compile
try:
    py_compile.compile('bot/main.py', doraise=True)
    print("✅ Синтаксис корректен!")
except py_compile.PyCompileError as e:
    print(f"❌ Ошибка синтаксиса: {e}")
