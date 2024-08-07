from datetime import datetime

from django.utils import timezone


def get_current_time():
    return timezone.localtime(timezone.now())


def datetimes_equal(dt1: datetime, dt2: datetime, format_: str) -> bool:
    return datetime.strptime(
        datetime.strftime(dt1, format_),
        format_,
    ) == datetime.strptime(
        datetime.strftime(dt2, format_),
        format_,
    )
