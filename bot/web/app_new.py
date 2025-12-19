from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
from sqlalchemy import select
from bot.models.init_db import db
from bot.models.database import User, Item, Car, Sale, Rental, CategoryEnum
from bot.utils.datetime_helper import get_moscow_now
from datetime import datetime, timedelta
import pytz
import asyncio

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)


@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')


def run_async(coro):
    """Вспомогательная функция для запуска async кода в синхронном контексте"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


@app.route('/api/add-item', methods=['POST'])
def add_item():
    """API для добавления товара"""
    try:
        data = request.json
        user_id = int(request.headers.get('X-User-ID', 0))
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User ID not provided'}), 400
        
        async def process():
            session = db.get_session()
            
            try:
                # Получаем или создаем пользователя
                user = await session.execute(
                    select(User).where(User.telegram_id == user_id)
                )
                user = user.scalar_one_or_none()
                
                if not user:
                    user = User(telegram_id=user_id)
                    session.add(user)
                    await session.flush()
                
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
                await session.commit()
                
                return {
                    'success': True,
                    'message': f'Товар "{data["name"]}" успешно добавлен!',
                    'item_id': item.id
                }
            finally:
                await session.close()
        
        result = run_async(process())
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/sell-item', methods=['POST'])
def sell_item():
    """API для продажи товара"""
    try:
        data = request.json
        item_id = int(data['item_id'])
        sale_price = float(data['price'])
        
        async def process():
            session = db.get_session()
            
            try:
                # Получаем товар
                item = await session.execute(
                    select(Item).where(Item.id == item_id)
                )
                item = item.scalar_one()
                
                # Помечаем как проданный
                item.sold = True
                
                # Добавляем запись о продаже
                sale = Sale(item_id=item_id, sale_price=sale_price)
                session.add(sale)
                await session.commit()
                
                profit = sale_price - item.purchase_price
                
                return {
                    'success': True,
                    'message': f'Товар продан за {sale_price}₽',
                    'profit': profit
                }
            finally:
                await session.close()
        
        result = run_async(process())
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/add-car', methods=['POST'])
def add_car():
    """API для добавления автомобиля"""
    try:
        data = request.json
        user_id = int(request.headers.get('X-User-ID', 0))
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User ID not provided'}), 400
        
        async def process():
            session = db.get_session()
            
            try:
                # Получаем пользователя
                user = await session.execute(
                    select(User).where(User.telegram_id == user_id)
                )
                user = user.scalar_one()
                
                # Создаем автомобиль
                car = Car(
                    user_id=user.id,
                    name=data['name'],
                    cost=float(data['cost'])
                )
                session.add(car)
                await session.commit()
                
                return {
                    'success': True,
                    'message': f'Автомобиль "{data["name"]}" успешно добавлен!',
                    'car_id': car.id
                }
            finally:
                await session.close()
        
        result = run_async(process())
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/rent-car', methods=['POST'])
def rent_car():
    """API для записи об аренде"""
    try:
        data = request.json
        user_id = int(request.headers.get('X-User-ID', 0))
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User ID not provided'}), 400
        
        async def process():
            session = db.get_session()
            
            try:
                # Получаем пользователя
                user = await session.execute(
                    select(User).where(User.telegram_id == user_id)
                )
                user = user.scalar_one()
                
                # Парсим время окончания
                tz = pytz.timezone('Europe/Moscow')
                now = get_moscow_now()
                
                end_time_str = data['end_time']
                if end_time_str.startswith('+'):
                    hours = int(end_time_str[1:])
                    rental_end = now + timedelta(hours=hours)
                else:
                    time_parts = end_time_str.split(':')
                    rental_end = now.replace(hour=int(time_parts[0]), minute=int(time_parts[1]), second=0)
                    if rental_end < now:
                        rental_end += timedelta(days=1)
                
                # Создаем запись об аренде
                rental = Rental(
                    user_id=user.id,
                    car_id=int(data['car_id']),
                    price_per_hour=float(data['price_per_hour']),
                    hours=int(data['hours']),
                    rental_end=rental_end
                )
                session.add(rental)
                await session.commit()
                
                total_income = float(data['price_per_hour']) * int(data['hours'])
                
                return {
                    'success': True,
                    'message': f'Аренда записана! Доход: {total_income}₽',
                    'income': total_income
                }
            finally:
                await session.close()
        
        result = run_async(process())
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/send-timer-notification', methods=['POST'])
def send_timer_notification():
    """API для отправки уведомления о завершении таймера в телеграм"""
    try:
        data = request.json
        user_id = int(request.headers.get('X-User-ID', 0))
        timer_name = data.get('timer_name', 'Таймер')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User ID not provided'}), 400
        
        async def process():
            from bot.models.database import User
            from bot.main import bot
            
            try:
                # Получаем пользователя из БД
                async with db.get_session() as session:
                    result = await session.execute(
                        select(User).where(User.telegram_id == user_id)
                    )
                    user = result.scalar_one_or_none()
                
                if user:
                    # Отправляем сообщение в телеграм
                    await bot.send_message(
                        user.telegram_id,
                        f'⏱️ <b>Таймер завершён!</b>\n\n'
                        f'Таймер "<b>{timer_name}</b>" завершил обратный отсчёт.\n'
                        f'⏰ <i>Пора действовать!</i>',
                        parse_mode='HTML'
                    )
                    return {'success': True, 'message': 'Notification sent'}
                else:
                    return {'success': False, 'error': 'User not found'}
            except Exception as e:
                print(f'Error sending timer notification: {e}')
                return {'success': False, 'error': str(e)}
        
        result = run_async(process())
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


def run_web_server(port=5000, cert_file=None, key_file=None):
    """Запустить веб-сервер с HTTPS"""
    ssl_context = None
    if cert_file and key_file:
        ssl_context = (cert_file, key_file)
    
    app.run(host='0.0.0.0', port=port, debug=False, ssl_context=ssl_context, use_reloader=False)

