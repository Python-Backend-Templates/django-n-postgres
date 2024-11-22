import functools
import logging
import warnings
from typing import Any, Callable, Dict, Literal, Type, TypeVar

from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django_redis.cache import RedisCache

from config import config

T = TypeVar("T")
TModel = TypeVar("TModel", bound=models.Model)
CacheResultType = Literal["instance", "queryset"]


MODEL_META_INSTANCES_CACHABLE_ATTR: str = "instances_cachable"
MODEL_META_QUERYSETS_CACHABLE_ATTR: str = "querysets_cachable"
MODEL_META_ATTR_BY_TYPE: Dict[CacheResultType, str] = {
    "instance": MODEL_META_INSTANCES_CACHABLE_ATTR,
    "queryset": MODEL_META_QUERYSETS_CACHABLE_ATTR,
}
MODEL_CACHE_OBJECTS_LIMIT: int = 1000
MODEL_CACHE_TTL: int = 60 * 5  # in seconds
MODEL_CACHE_INSTANCE_KEY_PATTERN: Callable[[str, str], str] = (
    lambda class_name, method: f"{class_name.lower()}::instance::{method}"
)
MODEL_CACHE_QUERYSET_KEY_PATTERN: Callable[[str, str], str] = (
    lambda class_name, method: f"{class_name.lower()}::queryset::{method}"
)


class CacheOnChange:
    def __init__(self, querysets_cachable: bool) -> None:
        self.querysets_cachable = querysets_cachable

    def __call__(self, instance: TModel, **kwargs: Any) -> None:
        from config.di import Container

        cache: RedisCache = Container.redis_cache()
        cache.set(
            f"{instance._meta.model_name}::{instance.pk}",
            instance,
            timeout=MODEL_CACHE_TTL,
        )
        # invalidate cached views
        cache.delete_pattern(f"*{config.CACHE_VIEW_KEY_PREFIX(instance.__class__)}*")
        # invalidate repositories instance caches
        cache.delete_pattern(
            MODEL_CACHE_INSTANCE_KEY_PATTERN(
                instance._meta.model_name, "*"  # type:ignore[arg-type]
            )
        )
        if self.querysets_cachable:
            # invalidate repositories queryset caches
            cache.delete_pattern(
                MODEL_CACHE_QUERYSET_KEY_PATTERN(
                    instance._meta.model_name, "*"  # type:ignore[arg-type]
                )
            )


class CacheOnDelete:
    def __init__(self, querysets_cachable: bool) -> None:
        self.querysets_cachable = querysets_cachable

    def __call__(self, instance: TModel, **kwargs: Any) -> None:
        from config.di import Container

        cache: RedisCache = Container.redis_cache()
        cache.delete(f"{instance._meta.model_name}::{instance.pk}")
        # invalidate cached views
        cache.delete_pattern(f"*{config.CACHE_VIEW_KEY_PREFIX(instance.__class__)}*")
        # invalidate repositories instance caches
        cache.delete_pattern(
            MODEL_CACHE_INSTANCE_KEY_PATTERN(
                instance._meta.model_name, "*"  # type:ignore[arg-type]
            )
        )
        if self.querysets_cachable:
            # invalidate repositories queryset caches
            cache.delete_pattern(
                MODEL_CACHE_QUERYSET_KEY_PATTERN(
                    instance._meta.model_name, "*"  # type:ignore[arg-type]
                )
            )


def cachable(
    cls: Type[TModel] | None = None,
    *,
    cache_querysets: bool = False,
) -> Callable:
    """
    ## This decorator can be used to make django model cachable.

    ### Limitations:
        - `config.CACHE_ENABLED` must be `True`
        - If `cache_querysets` is `True`, the number of rows in table
            must not exceed the limit of 1000 (`MODEL_CACHE_OBJECTS_LIMIT`).\n
            !!! This check is performed on app initialization, so if
            the number of rows exceeds limit in runtime,
            cache will still be enabled. To prevent that case,
            use decorator carefully, only on small sized tables. !!!

    ### If decorator is applied:
        - Model `Meta` class has an attribute `instances_cachable`
            (`MODEL_META_INSTANCES_CACHABLE_ATTR`),
            which is equals to `True`.
         - Model `Meta` class has an attribute `querysets_cachable`
            (`MODEL_META_QUERYSETS_CACHABLE_ATTR`), which is equals
            to `cache_querysets & (rows <= MODEL_CACHE_OBJECTS_LIMIT)`.
        - Receivers for update and delete events are connected via
            `post_save` and `pre_delete` signals respectively.
        - Update receiver updates cache value of instance and invalidates
            cache for querysets (both for views and repository methods).
        - Delete receiver deletes cache value of instance and invalidates
            cache for querysets (both for views and repository methods).

    ### Args:
        - cache_querysets: if `True`:
            - All model querysets are deleted from cache
                on any instance update or delete.
            - All results with type `queryset` are cached
                on @cache(type="queryset") decorator usage
    """

    def decorator(cls: Type[TModel]) -> Type[TModel]:
        def wrap(cls: Type[TModel]) -> Type[TModel]:
            if not config.CACHE_ENABLED:
                return cls

            setattr(cls._meta, MODEL_META_INSTANCES_CACHABLE_ATTR, True)

            querysets_cachable = cache_querysets
            if cache_querysets:
                with warnings.catch_warnings(action="ignore"):
                    if (
                        rows := cls.objects.count()  # type:ignore[attr-defined]
                    ) > MODEL_CACHE_OBJECTS_LIMIT:
                        logging.warning(
                            (
                                f"Caching querysets for model {cls._meta.model_name} "
                                "was not enabled due to exceeded limit "
                                f"({MODEL_CACHE_OBJECTS_LIMIT}) of rows: {rows}"
                            )
                        )
                        setattr(cls._meta, MODEL_META_QUERYSETS_CACHABLE_ATTR, False)
                        querysets_cachable = False
                    else:
                        setattr(cls._meta, MODEL_META_QUERYSETS_CACHABLE_ATTR, True)

            receiver(
                post_save, sender=cls, weak=False, dispatch_uid="on_change_callback"
            )(CacheOnChange(querysets_cachable=querysets_cachable))
            receiver(
                pre_delete, sender=cls, weak=False, dispatch_uid="on_delete_callback"
            )(CacheOnDelete(querysets_cachable=querysets_cachable))

            return cls

        return wrap(cls)

    if cls is not None:
        return decorator(cls)
    return decorator


def cache(
    func: Callable[..., T] | None = None,
    *,
    result_type: CacheResultType = "instance",
) -> Callable:
    """
    ## This decorator can be used to cache repository methods.
        Repository must be either `utils.repo.Repo` or its child.

    ### Method will be cached if each of below conditions are met:
        - `config.CACHE_ENABLED` is `True`;
        - Method belongs to repository of class `utils.repo.Repo` or its child;
        - Method belongs to repository of cachable model.
            Model is cachable if `@cachable` decorator is applied to it;
        - Method is not used with `for_update=True` keyword argument. In that case,
            method must always call database to select row for update.

    ### Supported cache backends:
        - Redis

    ### Args:
        - result_type:
            - `instance`: expect method to return model instance;
            - `queryset`: expect method to return model queryset.
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        from utils.repo import IRepo

        @functools.wraps(func)
        def wrapper(self: IRepo[TModel], *args: Any, **kwargs: Any) -> T:
            from config.di import Container
            from utils.repo import Repo

            if (
                not config.CACHE_ENABLED
                or not isinstance(self, Repo)
                or not getattr(
                    self.model_class._meta, MODEL_META_ATTR_BY_TYPE[result_type], False
                )
                or kwargs.get("for_update", False)
            ):
                return func(self, *args, **kwargs)

            def get_key() -> str:
                builder = {
                    "instance": MODEL_CACHE_INSTANCE_KEY_PATTERN,
                    "queryset": MODEL_CACHE_QUERYSET_KEY_PATTERN,
                }[result_type]

                return (
                    builder(self.model_class.__name__, func.__name__)
                    + f"?{'&'.join((*(str(arg) for arg in args), *(f'{k}={v}' for k, v in kwargs.items())))}"  # noqa:E501
                )

            cache: RedisCache = Container.redis_cache()
            key = get_key()
            cache_value = cache.get(key)
            if cache_value is not None:
                return cache_value
            actual_value = func(self, *args, **kwargs)
            cache.set(key, actual_value, timeout=MODEL_CACHE_TTL)
            return actual_value

        return wrapper

    if func is not None:
        return decorator(func)
    return decorator
