from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import pytz

from bot.models.database import User, Car, Rental
from bot.models.init_db import db
from bot.keyboards.keyboards import (
    get_rental_menu, get_back_keyboard, get_cancel_keyboard
)
from bot.utils.statistics import RentalStatistics
from bot.utils.datetime_helper import format_datetime, get_moscow_now

router = Router()


class AddCarStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_cost = State()


class RentCarStates(StatesGroup):
    waiting_for_price_per_hour = State()
    waiting_for_hours = State()
    waiting_for_end_time = State()


@router.callback_query(F.data == "rental_add_car")
async def add_car_start(callback: CallbackQuery, state: FSMContext):
    """Начало процесса добавления автомобиля"""
    await state.set_state(AddCarStates.waiting_for_name)
    await callback.message.edit_text(
        "🚗 Введите название автомобиля:",
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()


@router.message(AddCarStates.waiting_for_name)
async def receive_car_name(message: Message, state: FSMContext):
    """Получение названия автомобиля"""
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Добавление авто отменено", reply_markup=get_rental_menu())
        return
    
    await state.update_data(name=message.text)
    await state.set_state(AddCarStates.waiting_for_cost)
    await message.answer(
        "💰 Введите стоимость автомобиля (только число):",
        reply_markup=get_cancel_keyboard()
    )


@router.message(AddCarStates.waiting_for_cost)
async def receive_car_cost(message: Message, state: FSMContext):
    """Получение стоимости автомобиля"""
    try:
        cost = float(message.text)
        data = await state.get_data()
        
        session = db.get_session()
        try:
            # Получаем или создаем пользователя
            user = await session.execute(
                select(User).where(User.telegram_id == message.from_user.id)
            )
            user = user.scalar_one_or_none()
            
            if not user:
                user = User(telegram_id=message.from_user.id, username=message.from_user.username)
                session.add(user)
                await session.flush()
            
            # Создаем новый автомобиль
            car = Car(
                user_id=user.id,
                name=data['name'],
                cost=cost
            )
            session.add(car)
            await session.commit()
            
            await message.answer(
                f"✅ Автомобиль '{data['name']}' успешно добавлен!\n"
                f"Стоимость: {cost}₽",
                reply_markup=get_rental_menu()
            )
        finally:
            await session.close()
    except ValueError:
        await message.answer("❌ Введите корректное число!")
    
    await state.clear()


@router.callback_query(F.data == "rental_my_cars")
async def show_my_cars(callback: CallbackQuery):
    """Показать список моих автомобилей"""
    session = db.get_session()
    
    try:
        user = await session.execute(
            select(User).where(User.telegram_id == callback.from_user.id)
        )
        user = user.scalar_one_or_none()
        
        if not user:
            await callback.message.edit_text(
                "❌ У вас нет автомобилей",
                reply_markup=get_back_keyboard()
            )
            await callback.answer()
            return
        
        cars = await session.execute(
            select(Car).where(Car.user_id == user.id).order_by(Car.created_at.desc())
        )
        cars = cars.scalars().all()
        
        if not cars:
            await callback.message.edit_text(
                "❌ У вас нет автомобилей",
                reply_markup=get_back_keyboard()
            )
        else:
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            
            text = "🚗 Ваши автомобили:\n\n"
            for idx, car in enumerate(cars, 1):
                text += f"{idx}. {car.name}\n"
                text += f"   Стоимость: {car.cost}₽\n"
                text += f"   Добавлено: {format_datetime(car.created_at)}\n\n"
            
            # Создаем клавиатуру с автомобилями
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=f"🚗 {car.name}", callback_data=f"view_car_{car.id}")]
                for car in cars
            ] + [[InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]])
            
            await callback.message.edit_text(text, reply_markup=keyboard)
    finally:
        await session.close()
    
    await callback.answer()


@router.callback_query(F.data.startswith("view_car_"))
async def view_car_options(callback: CallbackQuery):
    """Показать опции для автомобиля"""
    car_id = int(callback.data.split("_")[2])
    
    session = db.get_session()
    try:
        car = await session.execute(select(Car).where(Car.id == car_id))
        car = car.scalar_one()
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        
        text = f"🚗 {car.name}\n"
        text += f"Стоимость: {car.cost}₽\n\n"
        text += "Выберите действие:"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💰 Сдал в аренду", callback_data=f"rent_car_{car_id}")],
            [InlineKeyboardButton(text="📊 Статистика", callback_data=f"car_stats_{car_id}")],
            [InlineKeyboardButton(text="🗑️ Удалить авто", callback_data=f"delete_car_{car_id}")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="rental_my_cars")],
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard)
    finally:
        await session.close()
    
    await callback.answer()


@router.callback_query(F.data.startswith("rent_car_"))
async def rent_car_start(callback: CallbackQuery, state: FSMContext):
    """Начало процесса сдачи автомобиля в аренду"""
    car_id = int(callback.data.split("_")[2])
    await state.update_data(rental_car_id=car_id)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да, уже прошла", callback_data="rental_is_past_yes"),
            InlineKeyboardButton(text="❌ Нет, текущая", callback_data="rental_is_past_no")
        ],
        [InlineKeyboardButton(text="↩️ Отмена", callback_data="cancel")]
    ])
    
    await callback.message.edit_text(
        "❓ Это аренда, которая уже прошла в прошлом?",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data.startswith("rental_is_past_"))
async def set_rental_is_past(callback: CallbackQuery, state: FSMContext):
    """Установить флаг прошедшей аренды"""
    is_past = callback.data == "rental_is_past_yes"
    await state.update_data(is_past=is_past)
    await state.set_state(RentCarStates.waiting_for_price_per_hour)
    
    await callback.message.edit_text(
        "💰 Введите цену за час (только число):",
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()


@router.message(RentCarStates.waiting_for_price_per_hour)
async def receive_rental_price(message: Message, state: FSMContext):
    """Получение цены за час"""
    try:
        price = float(message.text)
        await state.update_data(price_per_hour=price)
        await state.set_state(RentCarStates.waiting_for_hours)
        await message.answer(
            "⏰ Введите количество часов аренды (только число):",
            reply_markup=get_cancel_keyboard()
        )
    except ValueError:
        await message.answer("❌ Введите корректное число!")


@router.message(RentCarStates.waiting_for_hours)
async def receive_rental_hours(message: Message, state: FSMContext):
    """Получение количества часов"""
    try:
        hours = int(message.text)
        await state.update_data(hours=hours)
        await state.set_state(RentCarStates.waiting_for_end_time)
        await message.answer(
            "🕐 Введите время окончания аренды в формате (ЧЧ:ММ) или количество часов от текущего времени:\n"
            "Пример: 18:30 или +3 (для 3 часов от текущего времени)",
            reply_markup=get_cancel_keyboard()
        )
    except ValueError:
        await message.answer("❌ Введите корректное число!")


@router.message(RentCarStates.waiting_for_end_time)
async def receive_rental_end_time(message: Message, state: FSMContext):
    """Получение времени окончания аренды"""
    try:
        data = await state.get_data()
        text = message.text
        is_past = data.get('is_past', False)
        
        tz = pytz.timezone('Europe/Moscow')
        now = datetime.now(tz)
        
        # Если это прошлая аренда, время может быть в прошлом
        if is_past:
            # Просто парсим время без проверки на будущее
            time_parts = text.split(":")
            # Предполагаем дату сегодня
            start_date = now.date()
            start_time = tz.localize(datetime.combine(start_date, datetime.strptime(text, "%H:%M").time()))
            
            # Конец аренды = начало + hours
            end_time = start_time + timedelta(hours=data['hours'])
        else:
            # Текущая аренда - обычная парсинг
            if text.startswith("+"):
                hours_to_add = int(text[1:])
                end_time = now + timedelta(hours=hours_to_add)
                start_time = now
            else:
                time_parts = text.split(":")
                end_time = now.replace(hour=int(time_parts[0]), minute=int(time_parts[1]), second=0, microsecond=0)
                # Если время в прошлом, переносим на завтра
                if end_time < now:
                    end_time += timedelta(days=1)
                start_time = now
        
        session = db.get_session()
        try:
            # Получаем пользователя
            user = await session.execute(
                select(User).where(User.telegram_id == message.from_user.id)
            )
            user = user.scalar_one()
            
            # Создаем запись об аренде
            rental = Rental(
                user_id=user.id,
                car_id=data['rental_car_id'],
                price_per_hour=data['price_per_hour'],
                hours=data['hours'],
                rental_start=start_time,
                rental_end=end_time,
                is_past=is_past  # Устанавливаем флаг
            )
            session.add(rental)
            await session.commit()
            
            total_income = data['price_per_hour'] * data['hours']
            past_label = "📅 (прошлая аренда)" if is_past else ""
            await message.answer(
                f"✅ Автомобиль сдано в аренду! {past_label}\n"
                f"Цена: {data['price_per_hour']}₽/ч x {data['hours']} ч\n"
                f"Общий доход: {total_income}₽\n"
                f"Начало: {format_datetime(start_time)}\n"
                f"Окончание: {format_datetime(end_time)}",
                reply_markup=get_rental_menu()
            )
        finally:
            await session.close()
    except (ValueError, IndexError):
        await message.answer("❌ Введите корректное время!")
    
    await state.clear()


@router.callback_query(F.data.startswith("delete_car_"))
async def delete_car(callback: CallbackQuery):
    """Удалить автомобиль"""
    car_id = int(callback.data.split("_")[2])
    
    session = db.get_session()
    try:
        car = await session.execute(select(Car).where(Car.id == car_id))
        car = car.scalar_one()
        
        await session.delete(car)
        await session.commit()
        
        await callback.message.edit_text(
            f"✅ Автомобиль '{car.name}' удален",
            reply_markup=get_back_keyboard()
        )
    finally:
        await session.close()
    
    await callback.answer()


@router.callback_query(F.data.startswith("car_stats_"))
async def show_car_statistics_menu(callback: CallbackQuery, state: FSMContext):
    """Показать меню выбора периода для статистики по конкретному авто"""
    car_id = int(callback.data.split("_")[2])
    await state.update_data(stats_car_id=car_id)
    
    from bot.keyboards.keyboards import get_statistics_period_keyboard
    await callback.message.edit_text(
        "📈 Выберите период для статистики:",
        reply_markup=get_statistics_period_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("period_"))
async def show_car_statistics(callback: CallbackQuery, state: FSMContext):
    """Показать статистику по конкретному авто или по всем"""
    data = await state.get_data()
    car_id = data.get('stats_car_id')
    period = callback.data.split("_")[1]
    
    session = db.get_session()
    
    try:
        if car_id:
            # Статистика по конкретному авто
            income = await RentalStatistics.get_income_by_car(session, car_id, period)
            
            car = await session.execute(select(Car).where(Car.id == car_id))
            car = car.scalar_one()
            
            period_text = {
                "day": "за день",
                "week": "за неделю",
                "month": "за месяц",
                "all": "за всё время"
            }.get(period, "за всё время")
            
            text = f"📈 Статистика по {car.name} {period_text}:\n\n"
            text += f"💵 Доход: {income:.2f}₽"
            
            await callback.message.edit_text(text, reply_markup=get_back_keyboard())
        else:
            # Статистика по всем авто
            user = await session.execute(
                select(User).where(User.telegram_id == callback.from_user.id)
            )
            user = user.scalar_one_or_none()
            
            if not user:
                await callback.message.edit_text(
                    "❌ У вас нет данных",
                    reply_markup=get_back_keyboard()
                )
                await callback.answer()
                return
            
            income = await RentalStatistics.get_total_income(session, user.id, period)
            
            period_text = {
                "day": "за день",
                "week": "за неделю",
                "month": "за месяц",
                "all": "за всё время"
            }.get(period, "за всё время")
            
            text = f"📈 Статистика аренды {period_text}:\n\n"
            text += f"💵 Доход: {income:.2f}₽"
            
            await callback.message.edit_text(text, reply_markup=get_back_keyboard())
    finally:
        await session.close()
    
    await callback.answer()
