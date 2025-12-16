from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models.database import User, Item, Sale, CategoryEnum
from bot.models.init_db import db
from bot.keyboards.keyboards import (
    get_resell_menu, get_category_keyboard, get_back_keyboard, get_cancel_keyboard
)
from bot.utils.statistics import ResellStatistics
from bot.utils.datetime_helper import format_datetime, format_date, get_moscow_now

router = Router()


class AddItemStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_category = State()
    waiting_for_price = State()
    waiting_for_comment = State()
    waiting_for_photo = State()


class SellItemStates(StatesGroup):
    waiting_for_price = State()


@router.callback_query(F.data == "resell_add_item")
async def add_item_start(callback: CallbackQuery, state: FSMContext):
    """Начало процесса добавления товара"""
    await state.set_state(AddItemStates.waiting_for_name)
    await callback.message.edit_text(
        "📝 Введите название предмета:",
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()


@router.message(AddItemStates.waiting_for_name)
async def receive_item_name(message: Message, state: FSMContext):
    """Получение названия товара"""
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Добавление товара отменено", reply_markup=get_resell_menu())
        return
    
    await state.update_data(name=message.text)
    await state.set_state(AddItemStates.waiting_for_category)
    await message.answer("📂 Выберите категорию:", reply_markup=get_category_keyboard())


@router.callback_query(AddItemStates.waiting_for_category, F.data.startswith("category_"))
async def receive_item_category(callback: CallbackQuery, state: FSMContext):
    """Получение категории товара"""
    category_map = {
        "category_accessory": CategoryEnum.ACCESSORY,
        "category_thing": CategoryEnum.THING,
        "category_apartment": CategoryEnum.APARTMENT,
        "category_house": CategoryEnum.HOUSE,
        "category_car": CategoryEnum.CAR,
    }
    
    category = category_map.get(callback.data)
    await state.update_data(category=category)
    await state.set_state(AddItemStates.waiting_for_price)
    await callback.message.edit_text(
        "💰 Введите цену покупки (только число):",
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()


@router.message(AddItemStates.waiting_for_price)
async def receive_item_price(message: Message, state: FSMContext):
    """Получение цены товара"""
    try:
        price = float(message.text)
        await state.update_data(price=price)
        await state.set_state(AddItemStates.waiting_for_comment)
        await message.answer(
            "📄 Добавьте комментарий (или напишите 'Нет'):",
            reply_markup=get_cancel_keyboard()
        )
    except ValueError:
        await message.answer("❌ Введите корректное число!")


@router.message(AddItemStates.waiting_for_comment)
async def receive_item_comment(message: Message, state: FSMContext):
    """Получение комментария товара"""
    comment = None if message.text == "Нет" else message.text
    await state.update_data(comment=comment)
    await state.set_state(AddItemStates.waiting_for_photo)
    await message.answer(
        "📷 Загрузите фотографию (или напишите 'Нет'):",
        reply_markup=get_cancel_keyboard()
    )


@router.message(AddItemStates.waiting_for_photo)
async def receive_item_photo(message: Message, state: FSMContext):
    """Получение фотографии товара"""
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
        
        # Получаем file_id если загружена фотография
        photo_file_id = None
        if message.photo:
            photo_file_id = message.photo[-1].file_id
        
        # Создаем новый товар
        item = Item(
            user_id=user.id,
            name=data['name'],
            category=data['category'],
            purchase_price=data['price'],
            comment=data['comment'],
            photo_file_id=photo_file_id
        )
        session.add(item)
        await session.commit()
        
        await message.answer(
            f"✅ Товар '{data['name']}' успешно добавлен!\n"
            f"Категория: {data['category'].value}\n"
            f"Цена: {data['price']}₽",
            reply_markup=get_resell_menu()
        )
    finally:
        await session.close()
    
    await state.clear()


@router.callback_query(F.data == "resell_inventory")
async def show_inventory(callback: CallbackQuery, state: FSMContext):
    """Показать инвентарь товаров"""
    session = db.get_session()
    
    try:
        user = await session.execute(
            select(User).where(User.telegram_id == callback.from_user.id)
        )
        user = user.scalar_one_or_none()
        
        if not user:
            await callback.message.edit_text(
                "❌ У вас нет товаров",
                reply_markup=get_back_keyboard()
            )
            await callback.answer()
            return
        
        items = await session.execute(
            select(Item).where(Item.user_id == user.id).order_by(Item.purchase_date.desc())
        )
        items = items.scalars().all()
        
        if not items:
            await callback.message.edit_text(
                "❌ У вас нет товаров",
                reply_markup=get_back_keyboard()
            )
        else:
            text = "📋 Ваш инвентарь:\n\n"
            for idx, item in enumerate(items, 1):
                status = "✅ Продано" if item.sold else "⏳ На продажу"
                text += f"{idx}. {item.name} ({item.category.value})\n"
                text += f"   Куплено: {item.purchase_price}₽ ({format_date(item.purchase_date)})\n"
                text += f"   Статус: {status}\n"
                if item.sale:
                    text += f"   Продано: {item.sale.sale_price}₽\n"
                if item.comment:
                    text += f"   Комментарий: {item.comment}\n"
                text += "\n"
            
            # Создаем клавиатуру с товарами
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=f"{item.name}", callback_data=f"sell_item_{item.id}")]
                for item in items
            ] + [[InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]])
            
            await callback.message.edit_text(text, reply_markup=keyboard)
    finally:
        await session.close()
    
    await callback.answer()


@router.callback_query(F.data.startswith("sell_item_"))
async def sell_item_start(callback: CallbackQuery, state: FSMContext):
    """Начало процесса продажи товара"""
    item_id = int(callback.data.split("_")[2])
    await state.update_data(selling_item_id=item_id)
    await state.set_state(SellItemStates.waiting_for_price)
    await callback.message.edit_text(
        "💰 Введите цену продажи (только число):",
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()


@router.message(SellItemStates.waiting_for_price)
async def receive_sell_price(message: Message, state: FSMContext):
    """Получение цены продажи"""
    try:
        price = float(message.text)
        data = await state.get_data()
        item_id = data['selling_item_id']
        
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
            sale = Sale(item_id=item_id, sale_price=price)
            session.add(sale)
            await session.commit()
            
            profit = price - item.purchase_price
            await message.answer(
                f"✅ Товар '{item.name}' продан!\n"
                f"Цена продажи: {price}₽\n"
                f"Прибыль: {profit}₽",
                reply_markup=get_resell_menu()
            )
        finally:
            await session.close()
    except ValueError:
        await message.answer("❌ Введите корректное число!")
    
    await state.clear()
