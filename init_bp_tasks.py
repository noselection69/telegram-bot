"""Инициализация BP заданий в БД"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bot.models.database import Base, BPTask
from bot.config import DATABASE_URL

# Подготавливаем URL для синхронного подключения
if "postgresql" in DATABASE_URL or "postgres" in DATABASE_URL:
    SYNC_DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg", "postgresql+psycopg2")
    SYNC_DATABASE_URL = SYNC_DATABASE_URL.replace("postgresql+asyncpg", "postgresql")
    connect_args = {}
else:
    SYNC_DATABASE_URL = DATABASE_URL.replace("sqlite+aiosqlite", "sqlite")
    connect_args = {"check_same_thread": False}

engine = create_engine(SYNC_DATABASE_URL, connect_args=connect_args)
Session = sessionmaker(bind=engine)

# BP задания
BP_TASKS = [
    # Легкие
    {"name": "Сделать скриншот", "category": "Легкие", "bp_without_vip": 10, "bp_with_vip": 20},
    {"name": "Посетить магазин", "category": "Легкие", "bp_without_vip": 15, "bp_with_vip": 30},
    {"name": "Написать отзыв", "category": "Легкие", "bp_without_vip": 20, "bp_with_vip": 40},
    
    # Средние
    {"name": "Купить товар", "category": "Средние", "bp_without_vip": 30, "bp_with_vip": 60},
    {"name": "Пригласить друга", "category": "Средние", "bp_without_vip": 40, "bp_with_vip": 80},
    {"name": "Пройти опрос", "category": "Средние", "bp_without_vip": 35, "bp_with_vip": 70},
    
    # Тяжелые
    {"name": "Заказать премиум", "category": "Тяжелые", "bp_without_vip": 100, "bp_with_vip": 200},
    {"name": "Привести 3 друзей", "category": "Тяжелые", "bp_without_vip": 150, "bp_with_vip": 300},
    {"name": "Потратить 1000$", "category": "Тяжелые", "bp_without_vip": 200, "bp_with_vip": 400},
]

def init_bp_tasks():
    """Инициализировать BP задания"""
    session = Session()
    try:
        # Проверяем есть ли уже задания
        existing = session.query(BPTask).count()
        if existing > 0:
            print(f"✅ BP задания уже инициализированы ({existing} заданий)")
            return
        
        # Добавляем новые задания
        for task_data in BP_TASKS:
            task = BPTask(**task_data)
            session.add(task)
        
        session.commit()
        print(f"✅ Инициализировано {len(BP_TASKS)} BP заданий")
    except Exception as e:
        print(f"❌ Ошибка инициализации BP заданий: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    init_bp_tasks()
