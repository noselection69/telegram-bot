#!/usr/bin/env python3
"""
Скрипт для принудительного обновления BP tasks на PostgreSQL
Этот скрипт можно запустить после деплоя на Railway
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

print("🚀 BP Tasks PostgreSQL Updater")
print("=" * 80)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL not set!")
    print("   This script should be run on Railway with DATABASE_URL set")
    print("   Or set it manually: export DATABASE_URL=postgresql://...")
    sys.exit(1)

print(f"📍 DATABASE_URL: {DATABASE_URL[:60]}...")

# Конвертируем asyncpg URL в psycopg2 для синхронной работы
if "postgresql+asyncpg" in DATABASE_URL:
    print("   Converting asyncpg → psycopg2 for sync access...")
    SYNC_DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg", "postgresql+psycopg2")
else:
    SYNC_DATABASE_URL = DATABASE_URL

try:
    # Создаём синхронный engine
    engine = create_engine(SYNC_DATABASE_URL, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("\n✅ Connected to PostgreSQL successfully")
    
    # Проверяем существует ли таблица bp_tasks
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = 'bp_tasks'
            )
        """))
        table_exists = result.scalar()
    
    if not table_exists:
        print("❌ ERROR: bp_tasks table does not exist!")
        print("   Run migrations first: python migrate_postgresql.py")
        sys.exit(1)
    
    print("✅ Table 'bp_tasks' exists")
    
    # Импортируем модель ПОСЛЕ подключения
    from bot.models.database import BPTask
    
    # Считаем текущее количество
    existing = session.query(BPTask).count()
    print(f"\n📊 Current tasks in PostgreSQL: {existing}")
    
    if existing > 0:
        # Показываем что есть
        categories = {}
        for task in session.query(BPTask).all():
            cat = task.category
            if cat not in categories:
                categories[cat] = 0
            categories[cat] += 1
        
        print("   By category:")
        for cat, count in sorted(categories.items()):
            print(f"     - {cat}: {count}")
    
    # Если заданий меньше 50, перезаписываем
    if existing < 50:
        print(f"\n⚠️  Found old version! ({existing} < 50)")
        print("🔄 Clearing old tasks...")
        
        deleted = session.query(BPTask).delete()
        session.commit()
        print(f"   ✅ Deleted {deleted} old tasks")
        
        # Добавляем новые задания
        print("\n📝 Adding 59 new BP tasks...")
        
        bp_tasks_data = [
            # ЛЁГКИЕ (28 заданий)
            {"name": "3 часа в онлайне (можно выполнять многократно за день)", "category": "Легкие", "bp_without_vip": 2, "bp_with_vip": 4},
            {"name": "Нули в казино", "category": "Легкие", "bp_without_vip": 2, "bp_with_vip": 4},
            {"name": "Успешная тренировка в тире", "category": "Легкие", "bp_without_vip": 1, "bp_with_vip": 2},
            {"name": "Арендовать киностудию", "category": "Легкие", "bp_without_vip": 2, "bp_with_vip": 4},
            {"name": "Купить лотерейный билет", "category": "Легкие", "bp_without_vip": 1, "bp_with_vip": 2},
            {"name": "Выиграть гонку в картинге", "category": "Легкие", "bp_without_vip": 1, "bp_with_vip": 2},
            {"name": "Проехать 1 уличную гонку (ставка минимум 1000$)", "category": "Легкие", "bp_without_vip": 1, "bp_with_vip": 2},
            {"name": "Добавить 5 видео в кинотеатре", "category": "Легкие", "bp_without_vip": 1, "bp_with_vip": 2},
            {"name": "Посетить любой сайт в браузере", "category": "Легкие", "bp_without_vip": 1, "bp_with_vip": 2},
            {"name": "Зайти в любой канал в Brawl", "category": "Легкие", "bp_without_vip": 1, "bp_with_vip": 2},
            {"name": "Поставить лайк любой анкете в Match", "category": "Легкие", "bp_without_vip": 1, "bp_with_vip": 2},
            {"name": "Прокрутить за DP серебрянный, золотой или driver кейс", "category": "Легкие", "bp_without_vip": 10, "bp_with_vip": 20},
            {"name": "Кинуть мяч питомцу 15 раз", "category": "Легкие", "bp_without_vip": 2, "bp_with_vip": 4},
            {"name": "15 выполненных питомцем команд", "category": "Легкие", "bp_without_vip": 2, "bp_with_vip": 4},
            {"name": "Ставка в колесе удачи в казино (межсерверное колесо)", "category": "Легкие", "bp_without_vip": 3, "bp_with_vip": 6},
            {"name": "Проехать 1 станцию на метро", "category": "Легкие", "bp_without_vip": 2, "bp_with_vip": 4},
            {"name": "Починить деталь в автосервисе", "category": "Легкие", "bp_without_vip": 1, "bp_with_vip": 2},
            {"name": "Забросить 2 мяча в баскетболе", "category": "Легкие", "bp_without_vip": 1, "bp_with_vip": 2},
            {"name": "Забить 2 гола в футболе", "category": "Легкие", "bp_without_vip": 1, "bp_with_vip": 2},
            {"name": "Победить в армрестлинге", "category": "Легкие", "bp_without_vip": 1, "bp_with_vip": 2},
            {"name": "Победить в дартс", "category": "Легкие", "bp_without_vip": 1, "bp_with_vip": 2},
            {"name": "Поиграть 1 минуту в волейбол", "category": "Легкие", "bp_without_vip": 1, "bp_with_vip": 2},
            {"name": "Поиграть 1 минуту в настольный теннис", "category": "Легкие", "bp_without_vip": 1, "bp_with_vip": 2},
            {"name": "Поиграть 1 минуту в большой теннис", "category": "Легкие", "bp_without_vip": 1, "bp_with_vip": 2},
            {"name": "Сыграть в мафию в казино", "category": "Легкие", "bp_without_vip": 3, "bp_with_vip": 6},
            {"name": "Сделать платеж по лизингу", "category": "Легкие", "bp_without_vip": 1, "bp_with_vip": 2},
            {"name": "Посадить траву в теплице", "category": "Легкие", "bp_without_vip": 4, "bp_with_vip": 8},
            {"name": "Запустить переработку обезболивающих в лаборатории", "category": "Легкие", "bp_without_vip": 4, "bp_with_vip": 8},
            # СРЕДНИЕ (19 заданий)
            {"name": "25 действий на стройке", "category": "Средние", "bp_without_vip": 2, "bp_with_vip": 4},
            {"name": "25 действий в порту", "category": "Средние", "bp_without_vip": 2, "bp_with_vip": 4},
            {"name": "25 действий в шахте", "category": "Средние", "bp_without_vip": 2, "bp_with_vip": 4},
            {"name": "3 победы в Дэнс Баттлах", "category": "Средние", "bp_without_vip": 2, "bp_with_vip": 4},
            {"name": "20 подходов в тренажерном зале", "category": "Средние", "bp_without_vip": 1, "bp_with_vip": 2},
            {"name": "10 посылок на почте", "category": "Средние", "bp_without_vip": 1, "bp_with_vip": 2},
            {"name": "10 действий на ферме", "category": "Средние", "bp_without_vip": 1, "bp_with_vip": 2},
            {"name": "Потушить 25 'огоньков' пожарным", "category": "Средние", "bp_without_vip": 1, "bp_with_vip": 2},
            {"name": "Выполнить 3 заказа дальнобойщиком", "category": "Средние", "bp_without_vip": 2, "bp_with_vip": 4},
            {"name": "Выкопать 1 сокровище (не мусор)", "category": "Средние", "bp_without_vip": 1, "bp_with_vip": 2},
            {"name": "Выиграть 5 игр в тренировочном комплексе со ставкой (от 100$)", "category": "Средние", "bp_without_vip": 1, "bp_with_vip": 2},
            {"name": "Выиграть 3 любых игры на арене со ставкой (от 100$)", "category": "Средние", "bp_without_vip": 1, "bp_with_vip": 2},
            {"name": "2 круга на любом маршруте автобусника", "category": "Средние", "bp_without_vip": 2, "bp_with_vip": 4},
            {"name": "5 раз снять 100% шкуру с животных", "category": "Средние", "bp_without_vip": 2, "bp_with_vip": 4},
            {"name": "Закрыть 5 кодов в силовых структурах", "category": "Средние", "bp_without_vip": 2, "bp_with_vip": 4},
            {"name": "Произвести 1 арест в КПЗ", "category": "Средние", "bp_without_vip": 1, "bp_with_vip": 2},
            {"name": "Поймать 20 рыб", "category": "Средние", "bp_without_vip": 4, "bp_with_vip": 8},
            {"name": "Выполнить 2 квеста любых клубов", "category": "Средние", "bp_without_vip": 4, "bp_with_vip": 8},
            {"name": "Принять участие в двух аирдропах", "category": "Средние", "bp_without_vip": 4, "bp_with_vip": 8},
            # ТЯЖЁЛЫЕ (12 заданий)
            {"name": "Заказ материалов для бизнеса вручную (просто прожать вкл/выкл)", "category": "Тяжелые", "bp_without_vip": 1, "bp_with_vip": 2},
            {"name": "Два раза оплатить смену внешности у хирурга в EMS", "category": "Тяжелые", "bp_without_vip": 2, "bp_with_vip": 4},
            {"name": "7 закрашенных граффити", "category": "Тяжелые", "bp_without_vip": 1, "bp_with_vip": 2},
            {"name": "Сдать 5 контрабанды", "category": "Тяжелые", "bp_without_vip": 2, "bp_with_vip": 4},
            {"name": "Участие в каптах/бизварах", "category": "Тяжелые", "bp_without_vip": 1, "bp_with_vip": 2},
            {"name": "Сдать Хаммер с ВЗХ", "category": "Тяжелые", "bp_without_vip": 3, "bp_with_vip": 6},
            {"name": "5 выданных медкарт в EMS", "category": "Тяжелые", "bp_without_vip": 2, "bp_with_vip": 4},
            {"name": "Закрыть 15 вызовов в EMS", "category": "Тяжелые", "bp_without_vip": 2, "bp_with_vip": 4},
            {"name": "Отредактировать 40 объявлений в WN", "category": "Тяжелые", "bp_without_vip": 2, "bp_with_vip": 4},
            {"name": "Взломать 15 замков на ограблениях домов или автоугонах", "category": "Тяжелые", "bp_without_vip": 2, "bp_with_vip": 4},
            {"name": "Поставить на учет 2 автомобиля (для LSPD)", "category": "Тяжелые", "bp_without_vip": 1, "bp_with_vip": 2},
            {"name": "Выкупить двух человек из КПЗ", "category": "Тяжелые", "bp_without_vip": 2, "bp_with_vip": 4},
        ]
        
        for i, task_data in enumerate(bp_tasks_data, 1):
            task = BPTask(**task_data)
            session.add(task)
            if i % 10 == 0:
                print(f"   Added {i}/59...")
        
        session.commit()
        print(f"\n✅ Successfully added {len(bp_tasks_data)} tasks to PostgreSQL!")
        
        # Проверяем итог
        final_count = session.query(BPTask).count()
        categories = {}
        for task in session.query(BPTask).all():
            cat = task.category
            if cat not in categories:
                categories[cat] = 0
            categories[cat] += 1
        
        print(f"\n📊 Final result in PostgreSQL:")
        print(f"   Total: {final_count} tasks")
        for cat in ["Легкие", "Средние", "Тяжелые"]:
            if cat in categories:
                print(f"   - {cat}: {categories[cat]}")
    else:
        print(f"\n✅ PostgreSQL already has current version ({existing} >= 50)")
    
    session.close()
    print("\n✅ Update completed!")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
