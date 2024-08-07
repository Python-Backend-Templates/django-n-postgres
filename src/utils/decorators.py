import functools
from typing import TypeVar

from django.db.models import Model

T = TypeVar("T", bound=Model)


def swagger_safe(model: T):
    """
    Декоратор, который предотвращает запросы к базе данных при генерации документации.
    Используется для метода `get_queryset`.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            if getattr(self, "swagger_fake_view", False):
                return model.objects.none()
            return func(self, *args, **kwargs)

        return wrapper

    return decorator
