from datetime import datetime, date, time, tzinfo, UTC
from functools import reduce
from typing import Literal, Dict, Tuple

from django.utils import timezone

Precision = Literal["year", "month", "day", "hour", "minute", "second", "microsecond"]

PRECISION_MAP: Dict[Precision, Tuple[Precision, ...]] = {
    "year": ("month", "day", "hour", "minute", "second", "microsecond"),
    "month": ("day", "hour", "minute", "second", "microsecond"),
    "day": ("hour", "minute", "second", "microsecond"),
    "hour": ("minute", "second", "microsecond"),
    "minute": ("second", "microsecond"),
    "second": ("microsecond",),
    "microsecond": tuple(),
}


def timezone_now() -> datetime:
    """
    This is a wrapper for `django.utils.timezone.now`
    Can be used as default value for `models.DateTimeField`
    and still be patched in tests.
    """
    return timezone.now()


def get_current_time(tz: tzinfo | None = None) -> datetime:
    return timezone.localtime(timezone.now(), timezone=tz)


def with_timezone(dt: datetime, tz: tzinfo) -> datetime:
    return dt.replace(tzinfo=tz)


def datetimes_equal(dt1: datetime, dt2: datetime, format_: str) -> bool:
    return datetime.strptime(
        datetime.strftime(dt1, format_),
        format_,
    ) == datetime.strptime(
        datetime.strftime(dt2, format_),
        format_,
    )


def date_to_datetime(
    date_: date,
    time: time | None = None,
    tz: tzinfo = UTC,
) -> datetime:
    return datetime.combine(date_, time or datetime.min.time(), tz)


def datetime_to_precision(
    dt: datetime,
    precision: Precision,
    tz: tzinfo = UTC,
) -> datetime:
    # type ignore for misc here is actually a bug of mypy
    # https://github.com/python/mypy/issues/10023
    # P.S. arg-type might be bug in mypy as well
    return reduce(
        lambda a, x: a.replace(**{x: 0}),  # type:ignore[misc,arg-type]
        PRECISION_MAP[precision],
        dt,
    ).replace(tzinfo=tz)
