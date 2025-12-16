from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import logging
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bot.models.database import User, Item, Car, Sale, Rental, CategoryEnum
from bot.utils.datetime_helper import get_moscow_now
from bot.config import DATABASE_URL
from datetime import datetime, timedelta
import pytz

# Настройка логирования
logger = logging.getLogger(__name__)

# Получаем абсолютные пути
BASE_DIR = Path(__file__).parent
TEMPLATE_DIR = BASE_DIR / 'templates'
STATIC_DIR = BASE_DIR / 'static'

# Логируем пути для отладки
logger.info(f"BASE_DIR: {BASE_DIR}")
logger.info(f"TEMPLATE_DIR: {TEMPLATE_DIR} (exists: {TEMPLATE_DIR.exists()})")
logger.info(f"STATIC_DIR: {STATIC_DIR} (exists: {STATIC_DIR.exists()})")

app = Flask(__name__, template_folder=str(TEMPLATE_DIR), static_folder=str(STATIC_DIR))
CORS(app)

# Инициализируем синхронную БД для Flask
SYNC_DATABASE_URL = DATABASE_URL.replace("sqlite+aiosqlite", "sqlite")
sync_engine = create_engine(SYNC_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)


@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')


@app.route('/api/add-item', methods=['POST'])
def add_item():
    """API для добавления товара"""
    try:
        data = request.json
        user_id = int(request.headers.get('X-User-ID', 0))
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User ID not provided'}), 400
        
        session = SessionLocal()
        try:
            # Получаем или создаем пользователя
            user = session.query(User).filter(User.telegram_id == user_id).first()
            if not user:
                user = User(telegram_id=user_id)
                session.add(user)
                session.flush()
            
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
                'message': f'Товар продан за {sale_price}₽',
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
            now = get_moscow_now()
            
            end_time_str = data['end_time'].strip()
            logger.info(f"Parsing end_time: '{end_time_str}'")
            
            try:
                if end_time_str.startswith('+'):
                    hours = int(end_time_str[1:].strip())
                    rental_end = now + timedelta(hours=hours)
                else:
                    # Пробуем разные форматы
                    if ':' in end_time_str:
                        time_parts = end_time_str.split(':')
                    elif ' ' in end_time_str:
                        time_parts = end_time_str.split()
                    else:
                        raise ValueError("Invalid time format")
                    
                    hour = int(time_parts[0].strip())
                    minute = int(time_parts[1].strip()) if len(time_parts) > 1 else 0
                    rental_end = now.replace(hour=hour, minute=minute, second=0)
                    if rental_end < now:
                        rental_end += timedelta(days=1)
            except (ValueError, IndexError) as e:
                logger.error(f"Error parsing time: {e}")
                raise ValueError(f"Invalid time format: {end_time_str}")

            
            # Создаем запись об аренде
            rental = Rental(
                user_id=user.id,
                car_id=int(data['car_id']),
                price_per_hour=float(data['price_per_hour']),
                hours=int(data['hours']),
                rental_end=rental_end
            )
            session.add(rental)
            session.commit()
            
            total_income = float(data['price_per_hour']) * int(data['hours'])
            
            logger.info(f"Rental added successfully: {rental.id}")
            
            return jsonify({
                'success': True,
                'message': f'Аренда записана! Доход: {total_income}₽',
                'income': total_income
            })
        finally:
            session.close()
    
    except Exception as e:
        logger.error(f"Error in rent_car: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400


# === GET ENDPOINTS ===

@app.route('/api/get-cars', methods=['GET'])
def get_cars():
    """Получить список всех авто пользователя"""
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
            
            return jsonify({
                'success': True,
                'cars': [
                    {
                        'id': car.id,
                        'name': car.name,
                        'cost': float(car.cost)
                    }
                    for car in cars
                ]
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
                return jsonify({
                    'success': True,
                    'items': []
                })
            
            items = session.query(Item).filter(Item.user_id == user.id).all()
            
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
    """Получить историю продаж"""
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
                    'sales': [],
                    'total_income': 0,
                    'total_profit': 0,
                    'total_sales': 0
                })
            
            # Получаем все продажи для товаров пользователя
            sales = session.query(Sale).join(Item).filter(Item.user_id == user.id).all()
            
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
    """Получить активные аренды (только текущие)"""
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
            
            return jsonify({
                'success': True,
                'rentals': [
                    {
                        'id': rental.id,
                        'car_name': rental.car.name,
                        'price_per_hour': float(rental.price_per_hour),
                        'hours': rental.hours,
                        'rental_start': rental.rental_start.isoformat() if rental.rental_start else None,
                        'rental_end': rental.rental_end.isoformat() if rental.rental_end else None,
                        'total_income': float(rental.price_per_hour) * rental.hours
                    }
                    for rental in rentals
                ]
            })
        finally:
            session.close()
    except Exception as e:
        logger.error(f"Error getting rentals: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/get-rental-stats', methods=['GET'])
def get_rental_stats():
    """Получить статистику по арендам"""
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
                    'total_cars': 0,
                    'total_rentals': 0,
                    'total_income': 0
                })
            
            # Количество машин
            cars_count = session.query(Car).filter(Car.user_id == user.id).count()
            
            # Все аренды
            rentals = session.query(Rental).filter(Rental.user_id == user.id).all()
            total_rentals = len(rentals)
            total_income = sum(float(r.price_per_hour) * r.hours for r in rentals)
            
            return jsonify({
                'success': True,
                'total_cars': cars_count,
                'total_rentals': total_rentals,
                'total_income': total_income
            })
        finally:
            session.close()
    except Exception as e:
        logger.error(f"Error getting rental stats: {e}")
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


def run_web_server(port=5000, cert_file=None, key_file=None):
    """Запустить веб-сервер с HTTPS"""
    ssl_context = None
    if cert_file and key_file:
        ssl_context = (cert_file, key_file)
    
    app.run(host='0.0.0.0', port=port, debug=False, ssl_context=ssl_context, use_reloader=False)

