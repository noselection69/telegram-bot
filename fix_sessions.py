#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Исправление всех использований db.get_session()"""
import os
import re

files_to_fix = [
    'bot/handlers/resell.py',
    'bot/handlers/statistics.py', 
    'bot/handlers/rental.py',
    'bot/web/app_new.py'
]

def fix_session_usage(filepath):
    """Исправить использование session в файле"""
    if not os.path.exists(filepath):
        print(f"❌ Файл не найден: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ищем паттерн: session = db.get_session() \n async with session() as ...
    # И заменяем на: session_factory = db.get_session() \n async with session_factory() as session:
    
    original = content
    
    # Паттерн 1: session = db.get_session() с последующим async with session()
    pattern1 = r'session = db\.get_session\(\)\s*\n\s*async with session\(\) as s:'
    replacement1 = 'session_factory = db.get_session()\n        async with session_factory() as session:'
    content = re.sub(pattern1, replacement1, content)
    
    # Паттерн 2: простой session = db.get_session() (замена на вызов)
    # но нужно быть осторожным - заменяем только если после этого используется .execute()
    
    # Ищем блоки с session = db.get_session() и заменяем переменную
    lines = content.split('\n')
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Если нашли session = db.get_session()
        if 'session = db.get_session()' in line and 'session_factory' not in line:
            indent = len(line) - len(line.lstrip())
            # Заменяем на session_factory
            new_lines.append(' ' * indent + 'session_factory = db.get_session()')
            i += 1
            
            # Ищем async with session() as ...
            while i < len(lines):
                if 'async with session()' in lines[i]:
                    # Заменяем session() на session_factory()
                    new_lines.append(lines[i].replace('session()', 'session_factory()').replace('as s:', 'as session:'))
                    i += 1
                    break
                elif 'async with session() as' in lines[i]:
                    new_lines.append(lines[i].replace('session()', 'session_factory()'))
                    i += 1
                    break
                else:
                    new_lines.append(lines[i])
                    i += 1
        else:
            new_lines.append(line)
            i += 1
    
    content = '\n'.join(new_lines)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Исправлен: {filepath}")
        return True
    else:
        print(f"⏭️  Нет изменений: {filepath}")
        return False

# Исправляем все файлы
for filepath in files_to_fix:
    fix_session_usage(filepath)

print("\n✅ Все файлы обработаны!")
