import os
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

# Получаем URL из переменных окружения
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://web-production-70ac2.up.railway.app")


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Главное меню с вкладками"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Калькулятор перекупа"), KeyboardButton(text="🚗 Аренда")],
        ],
        resize_keyboard=True
    )
    return keyboard


def get_open_app_keyboard() -> InlineKeyboardMarkup:
    """Inline кнопка для открытия приложения"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📱 Открыть приложение", web_app=WebAppInfo(url=WEBHOOK_URL))],
        ]
    )
    return keyboard


def get_resell_menu() -> InlineKeyboardMarkup:
    """Меню калькулятора перекупа - только Web App кнопка"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📊 Открыть", web_app=WebAppInfo(url=f"{WEBHOOK_URL}/#resell"))],
        ]
    )
    return keyboard


def get_rental_menu() -> InlineKeyboardMarkup:
    """Меню управления арендой - только Web App кнопка"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚗 Открыть", web_app=WebAppInfo(url=f"{WEBHOOK_URL}/#rental"))],
        ]
    )
    return keyboard


def get_category_keyboard() -> InlineKeyboardMarkup:
    """Выбор категории товара"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Аксессуар", callback_data="category_accessory")],
            [InlineKeyboardButton(text="Вещь", callback_data="category_thing")],
            [InlineKeyboardButton(text="Квартира", callback_data="category_apartment")],
            [InlineKeyboardButton(text="Дом", callback_data="category_house")],
            [InlineKeyboardButton(text="Автомобиль", callback_data="category_car")],
        ]
    )
    return keyboard


def get_statistics_period_keyboard() -> InlineKeyboardMarkup:
    """Выбор периода для статистики"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="День", callback_data="period_day")],
            [InlineKeyboardButton(text="Неделя", callback_data="period_week")],
            [InlineKeyboardButton(text="Месяц", callback_data="period_month")],
            [InlineKeyboardButton(text="Всё время", callback_data="period_all")],
        ]
    )
    return keyboard


def get_back_keyboard() -> InlineKeyboardMarkup:
    """Кнопка назад"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")],
        ]
    )
    return keyboard


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Кнопка отмены"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")],
        ]
    )
    return keyboard
