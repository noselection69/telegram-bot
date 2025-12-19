from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
import os

from bot.keyboards.keyboards import get_main_keyboard, get_resell_menu, get_rental_menu, get_open_app_keyboard

router = Router()


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
