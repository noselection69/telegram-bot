from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from bot.models.database import Item, Sale, Rental, User
from bot.utils.datetime_helper import is_same_day, is_same_week, is_same_month, get_moscow_now


class ResellStatistics:
    @staticmethod
    async def get_income(session: AsyncSession, user_id: int, period: str = "all"):
        """Получить доход (сумму продаж) за период"""
        query = select(func.sum(Sale.sale_price)).join(
            Item, Sale.item_id == Item.id
        ).where(Item.user_id == user_id)
        
        if period != "all":
            # Фильтруем по дате продажи
            all_sales = await session.execute(
                select(Sale).join(Item, Sale.item_id == Item.id).where(Item.user_id == user_id)
            )
            sales = all_sales.scalars().all()
            
            now = get_moscow_now()
            filtered_sales = []
            
            for sale in sales:
                if period == "day" and is_same_day(sale.sale_date, now):
                    filtered_sales.append(sale.sale_price)
                elif period == "week" and is_same_week(sale.sale_date, now):
                    filtered_sales.append(sale.sale_price)
                elif period == "month" and is_same_month(sale.sale_date, now):
                    filtered_sales.append(sale.sale_price)
            
            return sum(filtered_sales) if filtered_sales else 0.0
        
        result = await session.execute(query)
        total = result.scalar()
        return total or 0.0
    
    @staticmethod
    async def get_expenses(session: AsyncSession, user_id: int, period: str = "all"):
        """Получить расходы (сумму покупок) за период"""
        all_items = await session.execute(
            select(Item).where(Item.user_id == user_id, Item.sold == True)
        )
        items = all_items.scalars().all()
        
        now = get_moscow_now()
        total = 0.0
        
        for item in items:
            if period == "all":
                total += item.purchase_price
            elif period == "day" and is_same_day(item.purchase_date, now):
                total += item.purchase_price
            elif period == "week" and is_same_week(item.purchase_date, now):
                total += item.purchase_price
            elif period == "month" and is_same_month(item.purchase_date, now):
                total += item.purchase_price
        
        return total
    
    @staticmethod
    async def get_profit(session: AsyncSession, user_id: int, period: str = "all"):
        """Получить прибыль (доход - расходы) за период"""
        income = await ResellStatistics.get_income(session, user_id, period)
        expenses = await ResellStatistics.get_expenses(session, user_id, period)
        return income - expenses


class RentalStatistics:
    @staticmethod
    async def get_income_by_car(session: AsyncSession, car_id: int, period: str = "all"):
        """Получить доход по конкретному автомобилю"""
        all_rentals = await session.execute(
            select(Rental).where(Rental.car_id == car_id)
        )
        rentals = all_rentals.scalars().all()
        
        now = get_moscow_now()
        total = 0.0
        
        for rental in rentals:
            income = rental.price_per_hour * rental.hours
            
            if period == "all":
                total += income
            elif period == "day" and is_same_day(rental.rental_start, now):
                total += income
            elif period == "week" and is_same_week(rental.rental_start, now):
                total += income
            elif period == "month" and is_same_month(rental.rental_start, now):
                total += income
        
        return total
    
    @staticmethod
    async def get_total_income(session: AsyncSession, user_id: int, period: str = "all"):
        """Получить общий доход с аренды по всем автомобилям"""
        all_rentals = await session.execute(
            select(Rental).where(Rental.user_id == user_id)
        )
        rentals = all_rentals.scalars().all()
        
        now = get_moscow_now()
        total = 0.0
        
        for rental in rentals:
            income = rental.price_per_hour * rental.hours
            
            if period == "all":
                total += income
            elif period == "day" and is_same_day(rental.rental_start, now):
                total += income
            elif period == "week" and is_same_week(rental.rental_start, now):
                total += income
            elif period == "month" and is_same_month(rental.rental_start, now):
                total += income
        
        return total
