# 💾 Примеры кода для быстрого копирования

Готовые к использованию примеры кода для частых задач.

---

## 🎮 Telegram Bot примеры

### Добавить новую команду

```python
# bot/handlers/myhandler.py

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()

@router.message(Command("mycommand"))
async def handle_mycommand(message: Message):
    await message.answer("Привет! Это новая команда")
    
# Затем зарегистрируйте в bot/main.py:
# dp.include_router(myhandler.router)
```

### Добавить кнопку

```python
# bot/keyboards/keyboards.py

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_my_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Кнопка 1")],
            [KeyboardButton(text="Кнопка 2")],
        ]
    )

# Использование:
# await message.answer("Выберите:", reply_markup=get_my_keyboard())
```

### FSM для ввода данных

```python
# bot/states/my_states.py

from aiogram.fsm.state import State, StatesGroup

class MyStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_city = State()

# Использование в обработчике:
# await state.set_state(MyStates.waiting_for_name)
```

---

## 🗄️ Database примеры

### Создать нового пользователя

```python
from bot.models import User
from bot.database import SessionLocal
from sqlalchemy import select

async def create_user(user_id: int, first_name: str):
    async with SessionLocal() as session:
        user = User(
            id=user_id,
            first_name=first_name,
        )
        session.add(user)
        await session.commit()
```

### Получить пользователя

```python
async def get_user(user_id: int):
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
```

### Получить все товары пользователя

```python
async def get_user_items(user_id: int):
    async with SessionLocal() as session:
        result = await session.execute(
            select(Item).where(Item.user_id == user_id)
        )
        return result.scalars().all()
```

### Обновить запись

```python
async def update_item(item_id: int, **kwargs):
    async with SessionLocal() as session:
        item = await session.get(Item, item_id)
        if item:
            for key, value in kwargs.items():
                setattr(item, key, value)
            await session.commit()
```

### Удалить запись

```python
async def delete_item(item_id: int):
    async with SessionLocal() as session:
        item = await session.get(Item, item_id)
        if item:
            await session.delete(item)
            await session.commit()
```

---

## 📊 Статистика примеры

### Рассчитать прибыль

```python
from datetime import datetime, timedelta
from bot.utils.timezone import get_moscow_time
from sqlalchemy import select, and_
import pytz

async def calculate_profit(user_id: int, days: int = 7):
    async with SessionLocal() as session:
        moscow_tz = pytz.timezone('Europe/Moscow')
        now = get_moscow_time()
        start_date = now - timedelta(days=days)
        
        result = await session.execute(
            select(func.sum(Sale.profit))
            .where(and_(
                Sale.user_id == user_id,
                Sale.created_at >= start_date
            ))
        )
        
        total_profit = result.scalar() or 0
        return total_profit
```

### Получить статистику по периодам

```python
async def get_stats(user_id: int):
    """Получить статистику по всем периодам"""
    today_profit = await calculate_profit(user_id, days=1)
    week_profit = await calculate_profit(user_id, days=7)
    month_profit = await calculate_profit(user_id, days=30)
    
    return {
        'today': today_profit,
        'week': week_profit,
        'month': month_profit,
    }
```

---

## 🌐 Web App (Flask) примеры

### Добавить новый API endpoint

```python
# bot/web/app.py

from flask import request, jsonify

@app.route('/api/my-endpoint', methods=['POST'])
async def my_endpoint():
    data = request.json
    user_id = int(request.headers.get('X-User-ID', 0))
    
    # Валидация
    if not data.get('name'):
        return {'success': False, 'message': 'Ошибка: название не указано'}, 400
    
    # Логика
    # ... ваш код ...
    
    return {
        'success': True,
        'message': 'Успешно!',
        'data': {...}
    }
```

### Получить данные из БД в Web App

```python
@app.route('/api/get-items', methods=['GET'])
async def get_items():
    user_id = int(request.headers.get('X-User-ID', 0))
    
    items = await get_user_items(user_id)
    
    return {
        'success': True,
        'items': [
            {
                'id': item.id,
                'name': item.name,
                'price': item.price,
                'category': item.category,
            }
            for item in items
        ]
    }
```

### Отправить ошибку

```python
return {
    'success': False,
    'message': 'Ошибка: что-то пошло не так',
    'error': str(e)
}, 400
```

---

## 🎨 HTML/CSS/JS примеры

### HTML форма

```html
<form id="myForm">
    <input 
        type="text" 
        name="name" 
        placeholder="Введите название"
        required
    >
    <input 
        type="number" 
        name="price" 
        placeholder="Введите цену"
        required
    >
    <button type="submit">Отправить</button>
</form>
```

### JavaScript обработчик формы

```javascript
document.getElementById('myForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData);
    
    try {
        const response = await fetch('/api/my-endpoint', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-User-ID': userId,
            },
            body: JSON.stringify(data),
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('Успешно!', 'success');
        } else {
            showNotification(result.message, 'error');
        }
    } catch (error) {
        showNotification('Ошибка: ' + error.message, 'error');
    }
});
```

### CSS для кнопки

```css
button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 16px;
    transition: all 0.3s ease;
}

button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
}

button:active {
    transform: translateY(0);
}
```

---

## 🚀 Развертывание примеры

### Heroku Procfile

```
web: python -m bot.main
```

### Docker Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "bot.main"]
```

### Docker Compose

```yaml
version: '3.9'

services:
  bot:
    build: .
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
    volumes:
      - ./bot_data.db:/app/bot_data.db
    restart: always
```

### Nginx конфиг

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

---

## 📝 Bash скрипты

### Резервная копия БД

```bash
#!/bin/bash
DATE=$(date +%Y-%m-%d_%H-%M-%S)
cp bot_data.db backup/bot_data_$DATE.db
echo "Резервная копия создана: backup/bot_data_$DATE.db"
```

### Запуск с логированием

```bash
#!/bin/bash
python -m bot.main >> logs/bot.log 2>&1 &
echo "Бот запущен в фоне"
echo "Логи: logs/bot.log"
```

### Обновление проекта

```bash
#!/bin/bash
git pull origin main
pip install -r requirements.txt --upgrade
systemctl restart bot
echo "Проект обновлен!"
```

---

## 🔧 Конфигурация примеры

### .env полный файл

```
BOT_TOKEN=1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefg
WEB_APP_URL=https://your-domain.com
WEB_APP_PORT=5000
DATABASE_URL=sqlite:///bot_data.db
LOG_LEVEL=INFO
```

### requirements.txt с комментариями

```
# Telegram Bot Framework
aiogram==3.4.1

# ORM
sqlalchemy==2.0.23

# Async DB
aiosqlite==0.22.0

# Environment variables
python-dotenv==1.0.0

# Timezone support
pytz==2024.1

# Web Server
flask==3.0.0
flask-cors==4.0.0

# Optional: Production server
gunicorn==21.2.0
```

---

## 🐛 Логирование примеры

### Простое логирование

```python
import logging

logger = logging.getLogger(__name__)

logger.info("Это информационное сообщение")
logger.warning("Это предупреждение")
logger.error("Это ошибка")
logger.debug("Это отладочная информация")
```

### Логирование в файл

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
```

### Логирование в API

```python
try:
    result = await do_something()
    logger.info(f"Успешно! Результат: {result}")
except Exception as e:
    logger.error(f"Ошибка: {str(e)}")
    raise
```

---

## ⚠️ Обработка ошибок примеры

### Try-Except для API

```python
try:
    # Опасная операция
    user = await get_user(user_id)
    if not user:
        return {'success': False, 'message': 'Пользователь не найден'}, 404
    
except SQLAlchemyError as e:
    logger.error(f"Ошибка БД: {str(e)}")
    return {'success': False, 'message': 'Ошибка базы данных'}, 500
    
except Exception as e:
    logger.error(f"Неожиданная ошибка: {str(e)}")
    return {'success': False, 'message': 'Неожиданная ошибка'}, 500
```

### Валидация данных

```python
def validate_price(price):
    try:
        price = float(price)
        if price <= 0:
            raise ValueError("Цена должна быть больше 0")
        if price > 1000000:
            raise ValueError("Цена слишком большая")
        return price
    except ValueError as e:
        return None, str(e)
```

---

## 🔐 Безопасность примеры

### Проверка пользователя

```python
def check_user_access(user_id: int, required_id: int) -> bool:
    """Проверить, может ли пользователь доступить к данным"""
    return user_id == required_id

# Использование:
if not check_user_access(user_id, item.user_id):
    return {'success': False, 'message': 'Доступ запрещен'}, 403
```

### SQL injection защита

```python
# ❌ ОПАСНО - не делайте так!
# query = f"SELECT * FROM item WHERE id = {item_id}"

# ✅ БЕЗОПАСНО - используйте параметризированные запросы
from sqlalchemy import select
result = await session.execute(
    select(Item).where(Item.id == item_id)
)
```

---

## 📱 Телеграм WebApp примеры

### Инициализация

```javascript
const tg = window.Telegram.WebApp;

// Готовость
tg.ready();

// Расширить Web App
tg.expand();

// Установить цвет заголовка
tg.setHeaderColor('#667eea');

// Установить цвет фона
tg.setBackgroundColor('#ffffff');

// Получить ID пользователя
const userId = tg.initDataUnsafe?.user?.id || 0;
const firstName = tg.initDataUnsafe?.user?.first_name || 'User';
```

### Главная кнопка

```javascript
// Показать главную кнопку
tg.MainButton.show();
tg.MainButton.setText('Отправить');

// Обработчик нажатия
tg.MainButton.onClick(() => {
    // Ваше действие
    tg.close();
});

// Скрыть кнопку
tg.MainButton.hide();
```

### Уведомления

```javascript
// Вибрация
tg.HapticFeedback.impactOccurred('light');
tg.HapticFeedback.impactOccurred('medium');
tg.HapticFeedback.impactOccurred('heavy');

// Нотификация
tg.showAlert('Это алерт!');
tg.showConfirm('Вы уверены?').then(confirmed => {
    if (confirmed) {
        // Пользователь согласился
    }
});

// Подтверждение
tg.showPopup({
    title: 'Заголовок',
    message: 'Сообщение',
    buttons: [
        {id: 'ok', type: 'ok', text: 'ОК'},
        {id: 'cancel', type: 'cancel', text: 'Отмена'}
    ]
});
```

---

## 📞 Полезные команды

```bash
# Запуск
python -m bot.main

# Установка зависимостей
pip install -r requirements.txt

# Создание виртуального окружения
python -m venv venv

# Активация окружения
source venv/bin/activate  # Linux/Mac

# Тестирование
pytest tests/

# Проверка синтаксиса
python -m py_compile bot/**/*.py

# Форматирование кода
black bot/

# Линтинг
flake8 bot/

# Docker сборка
docker build -t my-bot .

# Docker запуск
docker run -e BOT_TOKEN=... my-bot
```

---

**Версия:** 1.0  
**Последнее обновление:** Декабрь 2024  

**💡 Совет:** Скопируйте любой пример и адаптируйте под свои нужды!
