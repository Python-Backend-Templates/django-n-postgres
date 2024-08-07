# type: ignore

from dependency_injector import containers, providers
from django.conf import settings as django_settings
from django.core.cache import cache as _cache


class Container(containers.DeclarativeContainer):
    celery_app = providers.Object(_celery_app)
    cache = providers.Object(_cache)
