from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Enum, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

# Импортируем функцию для получения времени в Москве
def get_current_moscow_time():
    """Получить текущее время в Москве"""
    from bot.utils.datetime_helper import get_moscow_now
    return get_moscow_now()


class CategoryEnum(enum.Enum):
    ACCESSORY = "Аксессуар"
    THING = "Вещь"
    APARTMENT = "Квартира"
    HOUSE = "Дом"
    CAR = "Автомобиль"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)  # BigInteger для поддержки больших ID
    username = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    has_platinum_vip = Column(Boolean, default=False)  # Есть ли платинум VIP
    
    items = relationship("Item", back_populates="user", cascade="all, delete-orphan")
    cars = relationship("Car", back_populates="user", cascade="all, delete-orphan")
    rentals = relationship("Rental", back_populates="user", cascade="all, delete-orphan")
    buy_prices = relationship("BuyPrice", back_populates="user", cascade="all, delete-orphan")
    bp_completions = relationship("BPCompletion", back_populates="user", cascade="all, delete-orphan")


class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(Enum(CategoryEnum), nullable=False)
    purchase_price = Column(Float, nullable=False)
    purchase_date = Column(DateTime, default=datetime.utcnow)
    comment = Column(Text, nullable=True)
    photo_file_id = Column(String(255), nullable=True)
    sold = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="items")
    sale = relationship("Sale", back_populates="item", uselist=False, cascade="all, delete-orphan")


class Sale(Base):
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    sale_price = Column(Float, nullable=False)
    sale_date = Column(DateTime, default=get_current_moscow_time)  # Используем Московское время
    
    item = relationship("Item", back_populates="sale")


class Car(Base):
    __tablename__ = "cars"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    cost = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="cars")
    rentals = relationship("Rental", back_populates="car", cascade="all, delete-orphan")


class Rental(Base):
    __tablename__ = "rentals"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
    price_per_hour = Column(Float, nullable=False)
    hours = Column(Integer, nullable=False)
    rental_start = Column(DateTime, default=get_current_moscow_time)
    rental_end = Column(DateTime, nullable=False)
    is_past = Column(Boolean, default=False)  # Флаг для уже прошедших аренд
    notified = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="rentals")
    car = relationship("Car", back_populates="rentals")


class BuyPrice(Base):
    __tablename__ = "buy_prices"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=True)  # Связь с товаром
    seller_name = Column(String(255), nullable=True)  # Имя того, кто добавил цену
    item_name = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    price_text = Column(String(255), nullable=True)  # Оригинальный текст (300-350к, 5G и т.д.)
    sale_price = Column(Float, nullable=True)  # Цена продажи (заполняется при продаже)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="buy_prices")
    item = relationship("Item", backref="buy_price_record")


class BPTask(Base):
    """Задания для фарма BP"""
    __tablename__ = "bp_tasks"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False)  # "Легкие", "Средние", "Тяжелые"
    bp_without_vip = Column(Integer, nullable=False)  # BP без платинум VIP
    bp_with_vip = Column(Integer, nullable=False)    # BP с платинум VIP
    
    completions = relationship("BPCompletion", back_populates="task", cascade="all, delete-orphan")


class BPCompletion(Base):
    """Отслеживание выполнения BP заданий"""
    __tablename__ = "bp_completions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("bp_tasks.id"), nullable=False)
    completed_at = Column(DateTime, default=get_current_moscow_time)
    completed_date = Column(DateTime, nullable=False)  # Дата в Москве (для группировки по дням)
    is_completed = Column(Boolean, default=True)
    bp_earned = Column(Integer, nullable=False)  # Сколько BP получено (с учётом VIP)
    
    user = relationship("User")
    task = relationship("BPTask", back_populates="completions")