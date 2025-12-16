from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models.database import User
from bot.models.init_db import db
from bot.keyboards.keyboards import get_statistics_period_keyboard, get_back_keyboard
from bot.utils.statistics import ResellStatistics, RentalStatistics

router = Router()


@router.callback_query(F.data == "resell_statistics")
async def show_resell_statistics_menu(callback: CallbackQuery):
    """Показать меню выбора периода для статистики перекупа"""
    await callback.message.edit_text(
        "📈 Выберите период для статистики:",
        reply_markup=get_statistics_period_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("period_"))
async def show_resell_statistics(callback: CallbackQuery):
    """Показать статистику перекупа за выбранный период"""
    period = callback.data.split("_")[1]
    session = db.get_session()
    
    try:
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
        
        # Получаем статистику
        income = await ResellStatistics.get_income(session, user.id, period)
        expenses = await ResellStatistics.get_expenses(session, user.id, period)
        profit = await ResellStatistics.get_profit(session, user.id, period)
        
        period_text = {
            "day": "за день",
            "week": "за неделю",
            "month": "за месяц",
            "all": "за всё время"
        }.get(period, "за всё время")
        
        text = f"📈 Статистика {period_text}:\n\n"
        text += f"💵 Доход: {income:.2f}₽\n"
        text += f"💸 Расходы: {expenses:.2f}₽\n"
        text += f"📊 Прибыль: {profit:.2f}₽\n"
        
        if profit > 0:
            text += f"✅ Успешно!"
        elif profit < 0:
            text += f"⚠️ Убыток!"
        
        await callback.message.edit_text(text, reply_markup=get_back_keyboard())
    finally:
        await session.close()
    
    await callback.answer()


@router.callback_query(F.data == "resell_history")
async def show_sales_history(callback: CallbackQuery):
    """Показать историю продаж"""
    session = db.get_session()
    
    try:
        user = await session.execute(
            select(User).where(User.telegram_id == callback.from_user.id)
        )
        user = user.scalar_one_or_none()
        
        if not user:
            await callback.message.edit_text(
                "❌ История пуста",
                reply_markup=get_back_keyboard()
            )
            await callback.answer()
            return
        
        # Получаем все проданные товары
        from bot.models.database import Item
        from sqlalchemy import and_
        
        items = await session.execute(
            select(Item).where(
                and_(Item.user_id == user.id, Item.sold == True)
            ).order_by(Item.purchase_date.desc())
        )
        items = items.scalars().all()
        
        if not items:
            await callback.message.edit_text(
                "❌ История пуста",
                reply_markup=get_back_keyboard()
            )
        else:
            from bot.utils.datetime_helper import format_datetime
            
            text = "📜 История продаж:\n\n"
            total_profit = 0
            
            for idx, item in enumerate(items, 1):
                profit = item.sale.sale_price - item.purchase_price
                total_profit += profit
                status = "✅" if profit > 0 else "⚠️" if profit < 0 else "➖"
                
                text += f"{idx}. {item.name} ({item.category.value})\n"
                text += f"   Куплено: {item.purchase_price}₽ → Продано: {item.sale.sale_price}₽\n"
                text += f"   {status} Прибыль: {profit}₽\n"
                text += f"   Дата: {format_datetime(item.sale.sale_date)}\n\n"
            
            text += f"\n📊 Всего прибыль: {total_profit:.2f}₽"
            
            await callback.message.edit_text(text, reply_markup=get_back_keyboard())
    finally:
        await session.close()
    
    await callback.answer()


@router.callback_query(F.data == "rental_statistics")
async def show_rental_statistics_menu(callback: CallbackQuery):
    """Показать меню выбора периода для статистики аренды"""
    await callback.message.edit_text(
        "📈 Выберите период для статистики:",
        reply_markup=get_statistics_period_keyboard()
    )
    await callback.answer()
