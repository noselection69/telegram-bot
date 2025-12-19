from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
import os
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.keyboards import get_main_keyboard, get_resell_menu, get_rental_menu, get_open_app_keyboard
from bot.models.database import User
from bot.models.init_db import db

ADMIN_ID = 360028214


router = Router()


@router.message(F.commands(['myid']))
async def myid_handler(message: Message):
    """Показать свой Telegram ID"""
    await message.answer(f'Ваш ID: {message.from_user.id}')


@router.message(F.commands(['debug']))
async def debug_handler(message: Message):
    """Показать отладочную информацию"""
    import os
    web_app_url = os.getenv('WEB_APP_URL', 'NOT SET')
    webhook_url = os.getenv('WEBHOOK_URL', 'NOT SET')
    await message.answer(
        f'📊 Отладка:\n'
        f'WEB_APP_URL: {web_app_url}\n'
        f'WEBHOOK_URL: {webhook_url}\n'
        f'Ваш ID: {message.from_user.id}\n'
        f'Админ ID: {ADMIN_ID}'
    )


@router.message(F.text == "📊 Калькулятор перекупа")
async def show_resell_menu(message: Message):
    """Показать меню калькулятора перекупа"""
    await message.answer(
        "📊 Калькулятор перекупа",
        reply_markup=get_resell_menu()
    )


@router.message(F.text == "🚗 Аренда")
async def show_rental_menu(message: Message):
    """Показать меню управления арендой"""
    await message.answer(
        "🚗 Управление арендой автомобилей",
        reply_markup=get_rental_menu()
    )


@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    """Вернуться в главное меню"""
    await callback.message.edit_text(
        "🏠 Главное меню",
        reply_markup=get_main_keyboard()
    )
    await callback.answer()


@router.message(F.text == "/start")
async def start_handler(message: Message):
    """Обработчик команды /start - открывает WebApp сразу"""
    await message.answer(
        "👋 Добро пожаловать в бот управления финансами!\n\n"
        "📱 Нажми кнопку ниже, чтобы открыть приложение:",
        reply_markup=get_open_app_keyboard()
    )


@router.message(F.text == "/menu")
async def menu_handler(message: Message):
    """Обработчик команды /menu - показывает меню с кнопкой открытия приложения"""
    await message.answer(
        "� Главное меню\n\n"
        "Выберите действие:",
        reply_markup=get_open_app_keyboard()
    )


@router.message(F.commands(['msg']))
async def msg_handler(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer('Доступ запрещен!')
        return
    
    parts = message.text.split(' ', 1)
    if len(parts) < 2:
        await message.answer('Используйте: /msg текст')
        return
    
    text = parts[1]
    await message.answer(f'Отправляю...')
    
    try:
        session = db.get_session()
        async with session() as s:
            result = await s.execute(select(User))
            users = result.scalars().all()
        
        sent = 0
        for user in users:
            try:
                await message.bot.send_message(user.telegram_id, f'Уведомление: {text}')
                sent += 1
            except:
                pass
        
        await message.answer(f'Отправлено: {sent}')
    except Exception as e:
        await message.answer(f'Ошибка: {str(e)}')
