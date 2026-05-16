from datetime import datetime, timedelta


def days_between(dt1: datetime, dt2: datetime) -> int:
    return (dt2 - dt1).days


def get_week_range(base: datetime, offset_weeks: int = 0):
    """Return (start, end) datetime for the week offset_weeks from base."""
    start_of_week = base - timedelta(days=base.weekday())
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    start = start_of_week + timedelta(weeks=offset_weeks)
    end = start + timedelta(days=6, hours=23, minutes=59, seconds=59)
    return start, end


def format_datetime(dt: datetime, fmt: str = "%d.%m.%Y %H:%M") -> str:
    return dt.strftime(fmt)
