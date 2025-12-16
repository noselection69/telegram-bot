from datetime import datetime, timedelta
import pytz


def get_moscow_now():
    """Получить текущее время в московском часовом поясе"""
    tz = pytz.timezone('Europe/Moscow')
    return datetime.now(tz)


def format_datetime(dt: datetime) -> str:
    """Форматировать дату и время для вывода"""
    if dt.tzinfo is None:
        tz = pytz.timezone('Europe/Moscow')
        dt = dt.replace(tzinfo=pytz.UTC).astimezone(tz)
    return dt.strftime("%d.%m.%Y %H:%M")


def format_date(dt: datetime) -> str:
    """Форматировать только дату"""
    if dt.tzinfo is None:
        tz = pytz.timezone('Europe/Moscow')
        dt = dt.replace(tzinfo=pytz.UTC).astimezone(tz)
    return dt.strftime("%d.%m.%Y")


def is_same_day(dt1: datetime, dt2: datetime = None) -> bool:
    """Проверить, что две даты в один день"""
    if dt2 is None:
        dt2 = get_moscow_now()
    
    tz = pytz.timezone('Europe/Moscow')
    if dt1.tzinfo is None:
        dt1 = dt1.replace(tzinfo=pytz.UTC).astimezone(tz)
    if dt2.tzinfo is None:
        dt2 = dt2.replace(tzinfo=pytz.UTC).astimezone(tz)
    
    return dt1.date() == dt2.date()


def is_same_week(dt1: datetime, dt2: datetime = None) -> bool:
    """Проверить, что две даты в одну неделю"""
    if dt2 is None:
        dt2 = get_moscow_now()
    
    tz = pytz.timezone('Europe/Moscow')
    if dt1.tzinfo is None:
        dt1 = dt1.replace(tzinfo=pytz.UTC).astimezone(tz)
    if dt2.tzinfo is None:
        dt2 = dt2.replace(tzinfo=pytz.UTC).astimezone(tz)
    
    return dt1.isocalendar()[:2] == dt2.isocalendar()[:2]


def is_same_month(dt1: datetime, dt2: datetime = None) -> bool:
    """Проверить, что две даты в один месяц"""
    if dt2 is None:
        dt2 = get_moscow_now()
    
    tz = pytz.timezone('Europe/Moscow')
    if dt1.tzinfo is None:
        dt1 = dt1.replace(tzinfo=pytz.UTC).astimezone(tz)
    if dt2.tzinfo is None:
        dt2 = dt2.replace(tzinfo=pytz.UTC).astimezone(tz)
    
    return dt1.year == dt2.year and dt1.month == dt2.month
