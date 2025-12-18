from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import logging
import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from bot.models.database import User, Item, Car, Sale, Rental, BuyPrice, CategoryEnum, BPTask, BPCompletion
from bot.utils.datetime_helper import get_moscow_now
from bot.config import DATABASE_URL
from datetime import datetime, timedelta
import pytz

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем абсолютные пути
BASE_DIR = Path(__file__).parent
TEMPLATE_DIR = BASE_DIR / 'templates'
STATIC_DIR = BASE_DIR / 'static'

app = Flask(__name__, template_folder=str(TEMPLATE_DIR), static_folder=str(STATIC_DIR))
CORS(app)

# Инициализируем синхронную БД для Flask
try:
    import os
    
    logger.info(f"📊 Flask database configuration:")
    logger.info(f"   DATABASE_URL: {DATABASE_URL}")
    logger.info(f"   RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT', 'NOT SET')}")
    
    # Преобразуем для синхронного использования
    if "postgresql" in DATABASE_URL or "postgres" in DATABASE_URL:
        # PostgreSQL: преобразуем asyncpg -> psycopg2 для синхронного доступа
        SYNC_DATABASE_URL = DATABASE_URL
        # Заменяем asyncpg на psycopg2
        SYNC_DATABASE_URL = SYNC_DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
        # На случай если уже без диалекта
        if "+psycopg2" not in SYNC_DATABASE_URL and "postgresql://" in SYNC_DATABASE_URL:
            SYNC_DATABASE_URL = SYNC_DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://")
        
        logger.info(f"   Using PostgreSQL (psycopg2)")
        connect_args = {}
    else:
        # SQLite: локально
        SYNC_DATABASE_URL = DATABASE_URL
        if "+aiosqlite" in SYNC_DATABASE_URL:
            SYNC_DATABASE_URL = SYNC_DATABASE_URL.replace("sqlite+aiosqlite://", "sqlite:///")
        logger.info(f"   Using SQLite")
        connect_args = {"check_same_thread": False}
    
    logger.info(f"   SYNC_DATABASE_URL: {SYNC_DATABASE_URL}")
    sync_engine = create_engine(SYNC_DATABASE_URL, connect_args=connect_args)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
    
    # Создаём все таблицы
    from bot.models.database import Base
    Base.metadata.create_all(bind=sync_engine)
    logger.info("✅ Database tables created/verified")
    
    # Проверяем и добавляем новые колонки если их нет
    try:
        with sync_engine.connect() as connection:
            if "postgresql" in DATABASE_URL or "postgres" in DATABASE_URL:
                # PostgreSQL: используем information_schema
                result = connection.execute(
                    text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_name='rentals' AND column_name='is_past'
                    );
                    """)
                )
                has_is_past = result.scalar()
                
                if not has_is_past:
                    logger.info("🔧 Adding is_past column to rentals table (PostgreSQL)...")
                    connection.execute(
                        text("ALTER TABLE rentals ADD COLUMN is_past BOOLEAN DEFAULT false;")
                    )
                    connection.commit()
                    logger.info("✅ is_past column added to PostgreSQL")
                else:
                    logger.info("✅ is_past column already exists")
            else:
                # SQLite: используем PRAGMA
                result = connection.execute(
                    text("PRAGMA table_info(rentals)")
                )
                columns = [row[1] for row in result.fetchall()]
                has_is_past = 'is_past' in columns
                
                if not has_is_past:
                    logger.info("🔧 Adding is_past column to rentals table (SQLite)...")
                    connection.execute(
                        text("ALTER TABLE rentals ADD COLUMN is_past BOOLEAN DEFAULT 0;")
                    )
                    connection.commit()
                    logger.info("✅ is_past column added to SQLite")
                else:
                    logger.info("✅ is_past column already exists")
    except Exception as e:
        logger.error(f"❌ Error adding is_past column: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    # Проверяем и добавляем has_platinum_vip колонку если её нет (для PostgreSQL и SQLite)
    try:
        with sync_engine.connect() as connection:
            if "postgresql" in DATABASE_URL or "postgres" in DATABASE_URL:
                # PostgreSQL: используем information_schema
                result = connection.execute(
                    text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_name='users' AND column_name='has_platinum_vip'
                    );
                    """)
                )
                has_vip = result.scalar()
                
                if not has_vip:
                    logger.info("🔧 Adding has_platinum_vip column to users table (PostgreSQL)...")
                    connection.execute(
                        text("ALTER TABLE users ADD COLUMN has_platinum_vip BOOLEAN DEFAULT false;")
                    )
                    connection.commit()
                    logger.info("✅ has_platinum_vip column added to PostgreSQL")
                else:
                    logger.info("✅ has_platinum_vip column already exists")
            else:
                # SQLite: используем PRAGMA
                result = connection.execute(
                    text("PRAGMA table_info(users)")
                )
                columns = [row[1] for row in result.fetchall()]
                has_vip = 'has_platinum_vip' in columns
                
                if not has_vip:
                    logger.info("🔧 Adding has_platinum_vip column to users table (SQLite)...")
                    connection.execute(
                        text("ALTER TABLE users ADD COLUMN has_platinum_vip BOOLEAN DEFAULT 0;")
                    )
                    connection.commit()
                    logger.info("✅ has_platinum_vip column added to SQLite")
                else:
                    logger.info("✅ has_platinum_vip column already exists")
    except Exception as e:
        logger.error(f"❌ Error adding has_platinum_vip column: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    # Инициализируем BP задания
    try:
        session = SessionLocal()
        existing = session.query(BPTask).count()
        if existing == 0:
            logger.info("🔧 Initializing BP tasks...")
            bp_tasks_data = [
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
            for task_data in bp_tasks_data:
                task = BPTask(**task_data)
                session.add(task)
            session.commit()
            logger.info(f"✅ BP tasks initialized ({len(bp_tasks_data)} tasks)")
        else:
            logger.info(f"✅ BP tasks already exist ({existing} tasks)")
        session.close()
    except Exception as e:
        logger.warning(f"⚠️ Could not initialize BP tasks: {e}")
except Exception as e:
    logger.error(f"❌ Database error: {e}")
    import traceback
    logger.error(traceback.format_exc())
    SessionLocal = None


@app.before_request
def log_request():
    """Логируем все входящие запросы"""
    logger.info(f"📨 Incoming {request.method} {request.path}")
    logger.info(f"   Headers: {dict(request.headers)}")


@app.errorhandler(Exception)
def handle_error(e):
    """Обработчик всех ошибок"""
    logger.error(f"❌ ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
    print(f"❌ ERROR: {type(e).__name__}: {str(e)}", file=sys.stderr)
    sys.stderr.flush()
    return jsonify({'error': str(e), 'type': type(e).__name__}), 500


@app.errorhandler(404)
def handle_404(e):
    """Обработчик 404 ошибок"""
    logger.error(f"❌ 404 Not Found: {request.method} {request.path}")
    logger.error(f"   Available routes: {[str(rule) for rule in app.url_map.iter_rules() if 'api' in str(rule)]}")
    return jsonify({'error': 'Not Found', 'path': request.path}), 404

# Флаг для отслеживания, запущен ли бот
_bot_started = False


try:
    @app.route('/')
    def index():
        """Главная страница"""
        logger.info("✅ Rendering index.html")
        print("GET / called", file=sys.stderr)
        sys.stderr.flush()
        return render_template('index.html')
    print("✅ Route / registered", file=sys.stderr)
    sys.stderr.flush()
except Exception as e:
    print(f"❌ Error registering route /: {e}", file=sys.stderr)
    sys.stderr.flush()

@app.route('/health')
def health():
    """Healthcheck endpoint"""
    logger.info("✅ Healthcheck called")
    return jsonify({'status': 'ok', 'message': 'Flask is running'}), 200


@app.route('/api/add-item', methods=['POST'])
def add_item():
    """API для добавления товара"""
    try:
        data = request.json
        user_id = int(request.headers.get('X-User-ID', 0))
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User ID not provided'}), 400
        
        logger.info(f"💾 Adding item for user {user_id}: {data.get('name')}")
        
        session = SessionLocal()
        try:
            # Получаем или создаем пользователя
            user = session.query(User).filter(User.telegram_id == user_id).first()
            if not user:
                user = User(telegram_id=user_id)
                session.add(user)
                session.flush()
                logger.info(f"   Created new user: {user.id}")
            
            # Создаем товар
            item = Item(
                user_id=user.id,
                name=data['name'],
                category=CategoryEnum[data['category']],
                purchase_price=float(data['price']),
                comment=data.get('comment'),
                photo_file_id=data.get('photo_file_id')
            )
            session.add(item)
            session.commit()
            
            logger.info(f"✅ Item saved successfully: ID={item.id}, name={item.name}")
            
            return jsonify({
                'success': True,
                'message': f'Товар "{data["name"]}" успешно добавлен!',
                'item_id': item.id
            })
        finally:
            session.close()
        
    except Exception as e:
        logger.error(f"Error in add_item: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/sell-item', methods=['POST'])
def sell_item():
    """API для продажи товара"""
    try:
        data = request.json
        item_id = int(data['item_id'])
        sale_price = float(data['price'])
        
        session = SessionLocal()
        try:
            # Получаем товар
            item = session.query(Item).filter(Item.id == item_id).first()
            if not item:
                return jsonify({'success': False, 'error': 'Item not found'}), 404
            
            # Помечаем как проданный
            item.sold = True
            
            # Добавляем запись о продаже
            sale = Sale(item_id=item_id, sale_price=sale_price)
            session.add(sale)
            session.commit()
            
            profit = sale_price - item.purchase_price
            
            return jsonify({
                'success': True,
                'message': f'Товар продан за {sale_price}$',
                'profit': profit
            })
        finally:
            session.close()
    
    except Exception as e:
        logger.error(f"Error in sell_item: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/add-car', methods=['POST'])
def add_car():
    """API для добавления автомобиля"""
    try:
        logger.info(f"Received POST /api/add-car")
        
        data = request.json
        user_id = int(request.headers.get('X-User-ID', 0))
        
        if not user_id:
            logger.error("User ID not provided")
            return jsonify({'success': False, 'error': 'User ID not provided'}), 400
        
        if not data:
            logger.error("No JSON data provided")
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        session = SessionLocal()
        try:
            # Получаем пользователя или создаем
            user = session.query(User).filter(User.telegram_id == user_id).first()
            if not user:
                user = User(telegram_id=user_id)
                session.add(user)
                session.flush()
            
            # Создаем автомобиль
            car = Car(
                user_id=user.id,
                name=data['name'],
                cost=float(data['cost'])
            )
            session.add(car)
            session.commit()
            
            logger.info(f"Car added successfully: {car.id}")
            
            return jsonify({
                'success': True,
                'message': f'Автомобиль "{data["name"]}" успешно добавлен!',
                'car_id': car.id
            })
        finally:
            session.close()
    
    except Exception as e:
        logger.error(f"Error in add_car: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/rent-car', methods=['POST'])
def rent_car():
    """API для записи об аренде"""
    try:
        data = request.json
        user_id = int(request.headers.get('X-User-ID', 0))
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User ID not provided'}), 400
        
        session = SessionLocal()
        try:
            # Получаем пользователя или создаем
            user = session.query(User).filter(User.telegram_id == user_id).first()
            if not user:
                user = User(telegram_id=user_id)
                session.add(user)
                session.flush()
            
            # Парсим время окончания
            now_moscow = get_moscow_now()
            is_past = data.get('is_past', False)  # Флаг прошедшей аренды
            end_time_str = data.get('end_time', '').strip()
            
            logger.info(f"Parsing rental: is_past={is_past}, end_time='{end_time_str}'")
            
            # Преобразуем в UTC для сохранения в БД
            tz_utc = pytz.UTC
            
            try:
                if is_past:
                    # Для прошедшей аренды: начало = сейчас, конец = сейчас - 1 час (уже прошла)
                    # Или можно использовать сейчас как время окончания
                    rental_start_moscow = now_moscow - timedelta(hours=int(data['hours']) + 1)
                    rental_end_moscow = now_moscow
                else:
                    # Для текущей аренды
                    if not end_time_str:
                        raise ValueError("end_time is required for current rentals")
                    
                    if end_time_str.startswith('+'):
                        hours = int(end_time_str[1:].strip())
                        rental_end_moscow = now_moscow + timedelta(hours=hours)
                    else:
                        # Пробуем разные форматы
                        time_parts = end_time_str.split(':') if ':' in end_time_str else end_time_str.split()
                        hour = int(time_parts[0].strip())
                        minute = int(time_parts[1].strip()) if len(time_parts) > 1 else 0
                        rental_end_moscow = now_moscow.replace(hour=hour, minute=minute, second=0)
                        if rental_end_moscow < now_moscow:
                            rental_end_moscow += timedelta(days=1)
                    
                    rental_start_moscow = now_moscow
            except (ValueError, IndexError) as e:
                logger.error(f"Error parsing time: {e}")
                raise ValueError(f"Invalid time format: {end_time_str}")

            # Конвертируем в UTC для сохранения в БД
            rental_start_utc = rental_start_moscow.astimezone(tz_utc)
            rental_end_utc = rental_end_moscow.astimezone(tz_utc)
            
            # Создаем запись об аренде
            rental = Rental(
                user_id=user.id,
                car_id=int(data['car_id']),
                price_per_hour=float(data['price_per_hour']),
                hours=int(data['hours']),
                rental_start=rental_start_utc,
                rental_end=rental_end_utc,
                is_past=is_past  # Устанавливаем флаг прошедшей аренды
            )
            session.add(rental)
            session.commit()
            
            total_income = float(data['price_per_hour']) * int(data['hours'])
            past_label = " (прошлая аренда)" if is_past else ""
            
            logger.info(f"Rental added successfully: {rental.id}{past_label}")
            
            return jsonify({
                'success': True,
                'message': f'Аренда записана! Доход: {total_income}${past_label}',
                'income': total_income
            })
        finally:
            session.close()
    
    except Exception as e:
        logger.error(f"Error in rent_car: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 400


# === GET ENDPOINTS ===

@app.route('/api/get-cars', methods=['GET'])
def get_cars():
    """Получить список всех авто пользователя с окупаемостью"""
    try:
        user_id = int(request.headers.get('X-User-ID', 0))
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User ID not provided'}), 400
        
        session = SessionLocal()
        try:
            user = session.query(User).filter(User.telegram_id == user_id).first()
            
            if not user:
                return jsonify({
                    'success': True,
                    'cars': []
                })
            
            cars = session.query(Car).filter(Car.user_id == user.id).all()
            
            cars_list = []
            for car in cars:
                # Рассчитываем общий доход этого авто
                rentals = session.query(Rental).filter(Rental.car_id == car.id).all()
                total_income = sum(float(r.price_per_hour) * r.hours for r in rentals)
                
                # Рассчитываем процент окупаемости
                payback_percent = 0
                if car.cost > 0:
                    payback_percent = min(100, (total_income / car.cost) * 100)
                
                cars_list.append({
                    'id': car.id,
                    'name': car.name,
                    'cost': float(car.cost),
                    'total_income': total_income,
                    'payback_percent': round(payback_percent, 1),
                    'rentals_count': len(rentals)
                })
            
            return jsonify({
                'success': True,
                'cars': cars_list
            })
        finally:
            session.close()
    except Exception as e:
        logger.error(f"Error getting cars: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/get-items', methods=['GET'])
def get_items():
    """Получить список товаров пользователя"""
    try:
        user_id = int(request.headers.get('X-User-ID', 0))
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User ID not provided'}), 400
        
        session = SessionLocal()
        try:
            user = session.query(User).filter(User.telegram_id == user_id).first()
            
            if not user:
                logger.info(f"📭 No user found for telegram_id {user_id}")
                return jsonify({
                    'success': True,
                    'items': []
                })
            
            items = session.query(Item).filter(Item.user_id == user.id).all()
            logger.info(f"📦 Retrieved {len(items)} items for user {user_id}")
            
            return jsonify({
                'success': True,
                'items': [
                    {
                        'id': item.id,
                        'name': item.name,
                        'category': item.category.value,
                        'price': float(item.purchase_price),
                        'sold': item.sold
                    }
                    for item in items
                ]
            })
        finally:
            session.close()
    except Exception as e:
        logger.error(f"Error getting items: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/get-sales', methods=['GET'])
def get_sales():
    """Получить историю продаж с фильтрацией"""
    try:
        user_id = int(request.headers.get('X-User-ID', 0))
        time_filter = request.args.get('time_filter', 'all')  # day, week, all
        deal_filter = request.args.get('deal_filter', 'all')  # best, worst, all
        
        logger.info(f"📊 Statistics request: user_id={user_id}, time_filter={time_filter}, deal_filter={deal_filter}")
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User ID not provided'}), 400
        
        session = SessionLocal()
        try:
            user = session.query(User).filter(User.telegram_id == user_id).first()
            
            if not user:
                return jsonify({
                    'success': True,
                    'sales': [],
                    'total_income': 0,
                    'total_profit': 0,
                    'total_sales': 0
                })
            
            # Получаем все продажи для товаров пользователя
            sales = session.query(Sale).join(Item).filter(Item.user_id == user.id).all()
            
            # Фильтруем по времени
            if time_filter == 'day':
                from datetime import datetime, timedelta
                # Получаем начало дня в Москве
                today = get_moscow_now().replace(hour=0, minute=0, second=0, microsecond=0)
                # Получаем конец дня в Москве
                tomorrow = today + timedelta(days=1)
                
                logger.info(f"📅 Filtering for day: {today} to {tomorrow}")
                
                # Сравниваем без timezone для корректности
                sales = [s for s in sales if s.sale_date and 
                        today.replace(tzinfo=None) <= s.sale_date.replace(tzinfo=None) < tomorrow.replace(tzinfo=None)]
            elif time_filter == 'week':
                from datetime import datetime, timedelta
                week_ago = get_moscow_now() - timedelta(days=7)
                # Убираем timezone для корректного сравнения
                week_ago_naive = week_ago.replace(tzinfo=None)
                now_naive = get_moscow_now().replace(tzinfo=None)
                
                logger.info(f"📊 Filtering for week: {week_ago_naive} to {now_naive}")
                
                sales = [s for s in sales if s.sale_date and 
                        week_ago_naive <= s.sale_date.replace(tzinfo=None) <= now_naive]
            
            # Сортируем по типу сделок
            if deal_filter == 'best':
                sales = sorted(sales, key=lambda s: float(s.sale_price) - float(s.item.purchase_price), reverse=True)
            elif deal_filter == 'worst':
                sales = sorted(sales, key=lambda s: float(s.sale_price) - float(s.item.purchase_price))
            
            total_income = sum(float(sale.sale_price) for sale in sales)
            total_profit = sum(float(sale.sale_price) - float(sale.item.purchase_price) for sale in sales)
            
            return jsonify({
                'success': True,
                'sales': [
                    {
                        'id': sale.id,
                        'item_name': sale.item.name,
                        'sale_price': float(sale.sale_price),
                        'purchase_price': float(sale.item.purchase_price),
                        'profit': float(sale.sale_price) - float(sale.item.purchase_price),
                        'created_at': sale.sale_date.isoformat() if sale.sale_date else None
                    }
                    for sale in sales
                ],
                'total_income': total_income,
                'total_profit': total_profit,
                'total_sales': len(sales)
            })
        finally:
            session.close()
    except Exception as e:
        logger.error(f"Error getting sales: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/get-rentals', methods=['GET'])
def get_rentals():
    """Получить активные аренды (только текущие) с московским временем"""
    try:
        user_id = int(request.headers.get('X-User-ID', 0))
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User ID not provided'}), 400
        
        session = SessionLocal()
        try:
            user = session.query(User).filter(User.telegram_id == user_id).first()
            
            if not user:
                return jsonify({
                    'success': True,
                    'rentals': []
                })
            
            now = get_moscow_now()
            # Получаем только активные аренды (которые еще не закончились)
            rentals = session.query(Rental).filter(
                Rental.user_id == user.id,
                Rental.rental_end > now
            ).all()
            
            logger.info(f"📊 Found {len(rentals)} active rentals for user {user_id}")
            
            # Форматируем даты в московское время
            def format_moscow_time(dt):
                if not dt:
                    return None
                try:
                    tz_moscow = pytz.timezone('Europe/Moscow')
                    tz_utc = pytz.UTC
                    
                    # Если это naive datetime, предполагаем что это UTC (как мы сохраняем)
                    if dt.tzinfo is None:
                        dt = tz_utc.localize(dt)
                    
                    # Конвертируем в Moscow timezone
                    dt_moscow = dt.astimezone(tz_moscow)
                    return dt_moscow.strftime('%d.%m.%Y %H:%M')
                except Exception as e:
                    logger.error(f"❌ Error formatting date {dt}: {e}")
                    return str(dt)
            
            rentals_data = []
            for rental in rentals:
                rental_dict = {
                    'id': rental.id,
                    'car_name': rental.car.name,
                    'price_per_hour': float(rental.price_per_hour),
                    'hours': rental.hours,
                    'rental_start': format_moscow_time(rental.rental_start),
                    'rental_end': format_moscow_time(rental.rental_end),
                    'total_income': float(rental.price_per_hour) * rental.hours
                }
                logger.info(f"📝 Rental {rental.id}: start={rental_dict['rental_start']}, end={rental_dict['rental_end']}")
                rentals_data.append(rental_dict)
            
            return jsonify({
                'success': True,
                'rentals': rentals_data
            })
        finally:
            session.close()
    except Exception as e:
        logger.error(f"Error getting rentals: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/get-rental-stats', methods=['GET'])
def get_rental_stats():
    """Получить статистику по арендам с фильтрами по времени"""
    try:
        user_id = int(request.headers.get('X-User-ID', 0))
        time_filter = request.args.get('time_filter', 'all')  # day, week, all
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User ID not provided'}), 400
        
        session = SessionLocal()
        try:
            user = session.query(User).filter(User.telegram_id == user_id).first()
            
            if not user:
                return jsonify({
                    'success': True,
                    'total_cars': 0,
                    'total_rentals': 0,
                    'total_income': 0,
                    'cars_stats': []
                })
            
            # Получаем все аренды пользователя
            all_rentals = session.query(Rental).filter(Rental.user_id == user.id).all()
            
            # Фильтруем по времени
            now = get_moscow_now()
            if time_filter == 'day':
                today = now.replace(hour=0, minute=0, second=0, microsecond=0)
                tomorrow = today + timedelta(days=1)
                filtered_rentals = [r for r in all_rentals if r.rental_start and 
                                   today.replace(tzinfo=None) <= r.rental_start.replace(tzinfo=None) < tomorrow.replace(tzinfo=None)]
            elif time_filter == 'week':
                week_ago = now - timedelta(days=7)
                filtered_rentals = [r for r in all_rentals if r.rental_start and 
                                   r.rental_start.replace(tzinfo=None) >= week_ago.replace(tzinfo=None)]
            else:  # all
                filtered_rentals = all_rentals
            
            # Общая статистика
            total_rentals = len(filtered_rentals)
            total_income = sum(float(r.price_per_hour) * r.hours for r in filtered_rentals)
            
            # Статистика по каждому автомобилю
            cars_stats = {}
            for rental in filtered_rentals:
                car = rental.car
                if not car:
                    continue
                    
                car_key = f"{car.id}_{car.name}"
                if car_key not in cars_stats:
                    cars_stats[car_key] = {
                        'car_id': car.id,
                        'car_name': car.name,
                        'rentals_count': 0,
                        'total_hours': 0,
                        'total_income': 0
                    }
                
                cars_stats[car_key]['rentals_count'] += 1
                cars_stats[car_key]['total_hours'] += rental.hours
                cars_stats[car_key]['total_income'] += float(rental.price_per_hour) * rental.hours
            
            # Сортируем по доходу (по убыванию)
            cars_list = sorted(cars_stats.values(), key=lambda x: x['total_income'], reverse=True)
            
            # Количество машин
            cars_count = session.query(Car).filter(Car.user_id == user.id).count()
            
            return jsonify({
                'success': True,
                'total_cars': cars_count,
                'total_rentals': total_rentals,
                'total_income': total_income,
                'time_filter': time_filter,
                'cars_stats': cars_list
            })
        finally:
            session.close()
    except Exception as e:
        logger.error(f"Error getting rental stats: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/edit-rental/<int:rental_id>', methods=['PUT'])
def edit_rental(rental_id):
    """Редактировать аренду (цена и часы)"""
    try:
        user_id = int(request.headers.get('X-User-ID', 0))
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User ID not provided'}), 400
        
        data = request.json
        
        session = SessionLocal()
        try:
            rental = session.query(Rental).filter(Rental.id == rental_id).first()
            
            if not rental:
                return jsonify({'success': False, 'error': 'Rental not found'}), 404
            
            user = session.query(User).filter(User.telegram_id == user_id).first()
            if not user or rental.user_id != user.id:
                return jsonify({'success': False, 'error': 'Unauthorized'}), 403
            
            # Обновляем цену и часы
            old_price = rental.price_per_hour
            old_hours = rental.hours
            old_income = old_price * old_hours
            
            rental.price_per_hour = float(data['price_per_hour'])
            rental.hours = int(data['hours'])
            
            new_income = rental.price_per_hour * rental.hours
            
            session.commit()
            
            logger.info(f"Rental {rental_id} updated: {old_price}×{old_hours}=${old_income} → {rental.price_per_hour}×{rental.hours}=${new_income}")
            
            return jsonify({
                'success': True,
                'message': f'Аренда обновлена! Старый доход: {old_income}$, новый доход: {new_income}$'
            })
        finally:
            session.close()
    except Exception as e:
        logger.error(f"Error editing rental: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/delete-car/<int:car_id>', methods=['DELETE'])
def delete_car(car_id):
    """Удалить автомобиль"""
    try:
        user_id = int(request.headers.get('X-User-ID', 0))
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User ID not provided'}), 400
        
        session = SessionLocal()
        try:
            car = session.query(Car).filter(Car.id == car_id).first()
            
            if not car:
                return jsonify({'success': False, 'error': 'Car not found'}), 404
            
            user = session.query(User).filter(User.telegram_id == user_id).first()
            if not user or car.user_id != user.id:
                return jsonify({'success': False, 'error': 'Unauthorized'}), 403
            
            session.delete(car)
            session.commit()
            
            return jsonify({'success': True, 'message': 'Машина удалена'})
        finally:
            session.close()
    except Exception as e:
        logger.error(f"Error deleting car: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/delete-item/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """Удалить товар"""
    try:
        user_id = int(request.headers.get('X-User-ID', 0))
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User ID not provided'}), 400
        
        session = SessionLocal()
        try:
            item = session.query(Item).filter(Item.id == item_id).first()
            
            if not item:
                return jsonify({'success': False, 'error': 'Item not found'}), 404
            
            user = session.query(User).filter(User.telegram_id == user_id).first()
            if not user or item.user_id != user.id:
                return jsonify({'success': False, 'error': 'Unauthorized'}), 403
            
            session.delete(item)
            session.commit()
            
            return jsonify({'success': True, 'message': 'Товар удалён'})
        finally:
            session.close()
    except Exception as e:
        logger.error(f"Error deleting item: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400


# === ЦЕНЫ СКУПА (BUY PRICES) ===

@app.route('/api/get-buy-prices', methods=['GET'])
def get_buy_prices():
    """Получить ВСЕ цены скупа (общий список для всех пользователей)"""
    try:
        session = SessionLocal()
        try:
            # Получаем все цены, отсортированные по дате (новые первыми)
            prices = session.query(BuyPrice).order_by(BuyPrice.created_at.desc()).all()
            
            return jsonify({
                'success': True,
                'prices': [
                    {
                        'id': price.id,
                        'item_name': price.item_name,
                        'price': price.price,
                        'price_text': price.price_text,  # Добавляем оригинальный текст цены
                        'seller_name': price.seller_name or '📌 Неизвестно',
                        'created_at': price.created_at.isoformat()
                    }
                    for price in prices
                ]
            })
        finally:
            session.close()
    except Exception as e:
        logger.error(f"Error in get_buy_prices: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/add-buy-price', methods=['POST'])
def add_buy_price():
    """Добавить цену скупа"""
    try:
        data = request.json
        user_id = int(request.headers.get('X-User-ID', 0))
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User ID not provided'}), 400
        
        session = SessionLocal()
        try:
            user = session.query(User).filter(User.telegram_id == user_id).first()
            if not user:
                user = User(telegram_id=user_id)
                session.add(user)
                session.flush()
            
            # Получаем имя пользователя для отображения в списке
            seller_name = user.username or f"Пользователь {user_id}"
            
            price = BuyPrice(
                user_id=user.id,
                seller_name=seller_name,
                item_name=data['item_name'],
                price=float(data['price']),
                price_text=data.get('price_text')  # Сохраняем оригинальный текст
            )
            session.add(price)
            session.commit()
            
            return jsonify({'success': True, 'message': 'Цена добавлена'})
        finally:
            session.close()
    except Exception as e:
        logger.error(f"Error in add_buy_price: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/delete-buy-price/<int:price_id>', methods=['DELETE'])
def delete_buy_price(price_id):
    """Удалить цену скупа"""
    try:
        user_id = int(request.headers.get('X-User-ID', 0))
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User ID not provided'}), 400
        
        session = SessionLocal()
        try:
            price = session.query(BuyPrice).filter(BuyPrice.id == price_id).first()
            
            if not price:
                return jsonify({'success': False, 'error': 'Price not found'}), 404
            
            user = session.query(User).filter(User.telegram_id == user_id).first()
            if not user or price.user_id != user.id:
                return jsonify({'success': False, 'error': 'Unauthorized'}), 403
            
            session.delete(price)
            session.commit()
            
            return jsonify({'success': True, 'message': 'Цена удалена'})
        finally:
            session.close()
    except Exception as e:
        logger.error(f"Error deleting buy price: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/debug-db', methods=['GET'])
def debug_db():
    """Диагностика БД - проверяем конфигурацию и данные"""
    from bot.config import DATABASE_URL
    import os
    
    try:
        db_info = {
            'success': True,
            'database_url': DATABASE_URL[:50] + '...' if len(DATABASE_URL) > 50 else DATABASE_URL,
            'railway_environment': os.getenv("RAILWAY_ENVIRONMENT", "NOT_SET")
        }
        
        # Определяем тип БД
        if "postgresql" in DATABASE_URL or "postgres" in DATABASE_URL:
            db_info['db_type'] = 'PostgreSQL'
            db_info['persistent'] = True
        else:
            db_info['db_type'] = 'SQLite'
            db_info['persistent'] = False
        
        session = SessionLocal()
        try:
            items_count = session.query(Item).count()
            users_count = session.query(User).count()
            sales_count = session.query(Sale).count()
            buy_prices_count = session.query(BuyPrice).count()
        finally:
            session.close()
        
        db_info.update({
            'items_count': items_count,
            'users_count': users_count,
            'sales_count': sales_count,
            'buy_prices_count': buy_prices_count
        })
        
        return jsonify(db_info)
    except Exception as e:
        logger.error(f"Error in debug_db: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400


# === BP ENDPOINTS ===

@app.route('/api/get-bp-tasks', methods=['GET'])
def get_bp_tasks():
    """Получить все BP задания с информацией о выполнении"""
    try:
        user_id = int(request.headers.get('X-User-ID', 0))
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User ID not provided'}), 400
        
        session = SessionLocal()
        try:
            user = session.query(User).filter(User.telegram_id == user_id).first()
            
            if not user:
                user = User(telegram_id=user_id)
                session.add(user)
                session.flush()
            
            # Получаем сегодняшнюю дату (в Москве)
            now_moscow = get_moscow_now()
            today_start = now_moscow.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = now_moscow.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            # Получаем все задания, сгруппированные по категориям
            all_tasks = session.query(BPTask).all()
            
            tasks_by_category = {}
            for task in all_tasks:
                # Проверяем выполнено ли задание сегодня
                completion = session.query(BPCompletion).filter(
                    BPCompletion.user_id == user.id,
                    BPCompletion.task_id == task.id,
                    BPCompletion.completed_date >= today_start,
                    BPCompletion.completed_date <= today_end,
                    BPCompletion.is_completed == True
                ).first()
                
                if task.category not in tasks_by_category:
                    tasks_by_category[task.category] = []
                
                tasks_by_category[task.category].append({
                    'id': task.id,
                    'name': task.name,
                    'bp_without_vip': task.bp_without_vip,
                    'bp_with_vip': task.bp_with_vip,
                    'is_completed': completion is not None
                })
            
            return jsonify({
                'success': True,
                'tasks': tasks_by_category,
                'has_platinum_vip': user.has_platinum_vip
            })
        finally:
            session.close()
    except Exception as e:
        logger.error(f"Error getting BP tasks: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/toggle-bp-task/<int:task_id>', methods=['POST'])
def toggle_bp_task(task_id):
    """Отметить/убрать галочку с BP задания"""
    try:
        user_id = int(request.headers.get('X-User-ID', 0))
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User ID not provided'}), 400
        
        data = request.json or {}
        is_completed = data.get('is_completed', False)
        
        session = SessionLocal()
        try:
            user = session.query(User).filter(User.telegram_id == user_id).first()
            if not user:
                user = User(telegram_id=user_id)
                session.add(user)
                session.flush()
            
            task = session.query(BPTask).filter(BPTask.id == task_id).first()
            if not task:
                return jsonify({'success': False, 'error': 'Task not found'}), 404
            
            # Получаем сегодняшнюю дату (в Москве)
            now_moscow = get_moscow_now()
            today_start = now_moscow.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Ищем существующее выполнение
            completion = session.query(BPCompletion).filter(
                BPCompletion.user_id == user.id,
                BPCompletion.task_id == task_id,
                BPCompletion.completed_date >= today_start
            ).first()
            
            if is_completed:
                # Отмечаем как выполненное
                if not completion:
                    bp_earned = task.bp_with_vip if user.has_platinum_vip else task.bp_without_vip
                    completion = BPCompletion(
                        user_id=user.id,
                        task_id=task_id,
                        completed_date=today_start,
                        is_completed=True,
                        bp_earned=bp_earned
                    )
                    session.add(completion)
                    logger.info(f"BP task {task_id} marked as completed for user {user_id} (+{bp_earned} BP)")
                else:
                    completion.is_completed = True
            else:
                # Убираем галочку
                if completion:
                    completion.is_completed = False
                    logger.info(f"BP task {task_id} marked as uncompleted for user {user_id}")
            
            session.commit()
            
            # Считаем сегодняшний BP
            today_bp = session.query(BPCompletion).filter(
                BPCompletion.user_id == user.id,
                BPCompletion.completed_date >= today_start,
                BPCompletion.is_completed == True
            ).all()
            
            total_bp_today = sum(c.bp_earned for c in today_bp)
            
            return jsonify({
                'success': True,
                'bp_earned': completion.bp_earned if is_completed and completion else 0,
                'total_bp_today': total_bp_today
            })
        finally:
            session.close()
    except Exception as e:
        logger.error(f"Error toggling BP task: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/get-bp-stats', methods=['GET'])
def get_bp_stats():
    """Получить статистику BP (за день, неделю, всё время)"""
    try:
        user_id = int(request.headers.get('X-User-ID', 0))
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User ID not provided'}), 400
        
        session = SessionLocal()
        try:
            user = session.query(User).filter(User.telegram_id == user_id).first()
            
            if not user:
                return jsonify({
                    'success': True,
                    'bp_today': 0,
                    'bp_week': 0,
                    'bp_total': 0
                })
            
            now_moscow = get_moscow_now()
            
            # За сегодня (с 07:00)
            today_07 = now_moscow.replace(hour=7, minute=0, second=0, microsecond=0)
            if now_moscow.hour < 7:
                today_07 -= timedelta(days=1)
            
            # За неделю
            week_start = now_moscow - timedelta(days=7)
            
            bp_today = session.query(BPCompletion).filter(
                BPCompletion.user_id == user.id,
                BPCompletion.completed_at >= today_07,
                BPCompletion.is_completed == True
            ).all()
            
            bp_week = session.query(BPCompletion).filter(
                BPCompletion.user_id == user.id,
                BPCompletion.completed_at >= week_start,
                BPCompletion.is_completed == True
            ).all()
            
            bp_total = session.query(BPCompletion).filter(
                BPCompletion.user_id == user.id,
                BPCompletion.is_completed == True
            ).all()
            
            return jsonify({
                'success': True,
                'bp_today': sum(c.bp_earned for c in bp_today),
                'bp_week': sum(c.bp_earned for c in bp_week),
                'bp_total': sum(c.bp_earned for c in bp_total)
            })
        finally:
            session.close()
    except Exception as e:
        logger.error(f"Error getting BP stats: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/toggle-platinum-vip', methods=['POST'])
def toggle_platinum_vip():
    """Включить/выключить платинум VIP"""
    try:
        user_id = int(request.headers.get('X-User-ID', 0))
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User ID not provided'}), 400
        
        data = request.json or {}
        has_vip = data.get('has_platinum_vip', False)
        
        session = SessionLocal()
        try:
            user = session.query(User).filter(User.telegram_id == user_id).first()
            if not user:
                user = User(telegram_id=user_id, has_platinum_vip=has_vip)
                session.add(user)
            else:
                user.has_platinum_vip = has_vip
            
            session.commit()
            logger.info(f"User {user_id} platinum VIP set to {has_vip}")
            
            return jsonify({
                'success': True,
                'has_platinum_vip': user.has_platinum_vip
            })
        finally:
            session.close()
    except Exception as e:
        logger.error(f"Error toggling platinum VIP: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 400


def run_web_server(port=5000, cert_file=None, key_file=None):
    """Запустить веб-сервер с HTTPS"""
    try:
        ssl_context = None
        if cert_file and key_file:
            ssl_context = (cert_file, key_file)
        
        logger.info(f"🚀 Starting Flask web server on 0.0.0.0:{port}")
        logger.info(f"   SSL: {'Enabled' if ssl_context else 'Disabled'}")
        logger.info(f"   Debug: False")
        
        # Важно: use_reloader=False чтобы не было двойного запуска в production
        app.run(host='0.0.0.0', port=port, debug=False, ssl_context=ssl_context, use_reloader=False)
        
    except Exception as e:
        logger.error(f"❌ Flask server error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise


# Финальная проверка при импорте
logger.info(f"✅ Flask app is ready! Routes: {len(app.url_map._rules)} routes registered")
logger.info(f"   Routes: {[str(rule) for rule in app.url_map.iter_rules()][:5]}...")
print("✅ bot.web.app module loaded successfully!", file=sys.stderr)
sys.stderr.flush()


