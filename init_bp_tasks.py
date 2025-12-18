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

# 59 BP заданий (28 легких + 19 средних + 12 тяжелых)
BP_TASKS = [
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

def init_bp_tasks():
    """Инициализировать BP задания"""
    session = Session()
    try:
        # Проверяем есть ли уже задания
        existing = session.query(BPTask).count()
        if existing >= 50:  # Если уже есть 50+ заданий (новые), то не обновляем
            print(f"✅ BP задания уже инициализированы ({existing} заданий)")
            return
        
        # Если старые задания (< 50), очищаем и добавляем новые
        if existing > 0:
            print(f"🔄 Обнаружены старые задания ({existing}), обновляем...")
            session.query(BPTask).delete()
            session.commit()
        
        # Добавляем новые задания
        for task_data in BP_TASKS:
            task = BPTask(**task_data)
            session.add(task)
        
        session.commit()
        print(f"✅ Инициализировано {len(BP_TASKS)} BP заданий (28 легких + 19 средних + 12 тяжелых)")
    except Exception as e:
        print(f"❌ Ошибка инициализации BP заданий: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    init_bp_tasks()
