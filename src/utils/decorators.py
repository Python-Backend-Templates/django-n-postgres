import functools
from typing import Any, Callable, Type, TypeVar

from django.db.models import Model, QuerySet
from django.views import View

TModel = TypeVar("TModel", bound=Model)


def swagger_safe(model: Type[TModel]) -> Callable:
    """
    Декоратор, который предотвращает запросы к базе данных при генерации документации.
    Используется для метода `get_queryset`.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self: View, *args: Any, **kwargs: Any) -> QuerySet[TModel]:
            if getattr(self, "swagger_fake_view", False):
                return model.objects.none()  # type: ignore[attr-defined]
            return func(self, *args, **kwargs)

        return wrapper

    return decorator
