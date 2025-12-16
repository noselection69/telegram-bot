import asyncio
import logging
from datetime import datetime
import pytz
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models.database import Rental, Car, User
from bot.models.init_db import db
from bot.utils.datetime_helper import get_moscow_now

logger = logging.getLogger(__name__)


async def check_rental_notifications(bot):
    """Проверить окончившиеся аренды и отправить уведомления"""
    while True:
        try:
            session = db.get_session()
            
            # Получаем все неуведомленные аренды, время которых истекло
            rentals = await session.execute(
                select(Rental).where(Rental.notified == False)
            )
            rentals = rentals.scalars().all()
            
            now = get_moscow_now()
            
            for rental in rentals:
                # Преобразуем rental_end к московскому времени для корректного сравнения
                tz = pytz.timezone('Europe/Moscow')
                rental_end = rental.rental_end
                if rental_end.tzinfo is None:
                    rental_end = rental_end.replace(tzinfo=pytz.UTC).astimezone(tz)
                
                if now >= rental_end:
                    # Получаем информацию о машине и пользователе
                    car = await session.execute(
                        select(Car).where(Car.id == rental.car_id)
                    )
                    car = car.scalar_one()
                    
                    user = await session.execute(
                        select(User).where(User.id == rental.user_id)
                    )
                    user = user.scalar_one()
                    
                    message_text = (
                        f"✅ Автомобиль вернулся с аренды!\n\n"
                        f"🚗 Автомобиль: {car.name}\n"
                        f"💰 Цена за час: {rental.price_per_hour}₽\n"
                        f"⏰ Количество часов: {rental.hours}\n"
                        f"💵 Общий доход: {rental.price_per_hour * rental.hours}₽\n"
                        f"🕐 Время окончания: {rental.rental_end.strftime('%d.%m.%Y %H:%M')}"
                    )
                    
                    try:
                        await bot.send_message(
                            chat_id=user.telegram_id,
                            text=message_text
                        )
                        
                        # Помечаем как уведомленного
                        rental.notified = True
                        await session.commit()
                        logger.info(f"Notification sent for rental {rental.id}")
                    except Exception as e:
                        logger.error(f"Failed to send notification: {e}")
            
            await session.close()
        except Exception as e:
            logger.error(f"Error in rental notification check: {e}")
        
        # Проверяем каждые 60 секунд
        await asyncio.sleep(60)
