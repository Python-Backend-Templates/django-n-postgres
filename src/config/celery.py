import logging
import os
from pathlib import Path

from celery import Celery, signals
from django.conf import settings

from . import config

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@signals.setup_logging.connect
def on_celery_setup_logging(**kwargs):
    try:
        Path(settings.LOG_PATH + "celery").mkdir(parents=False, exist_ok=True)
    except (FileExistsError, FileNotFoundError):
        pass
    config_ = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "{levelname} {asctime}: {message}",
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "style": "{",
            },
            "json": {
                "()": "utils.logging.JsonLogFormatter",
            },
        },
        "handlers": {
            "errors": {
                "level": "ERROR",
                "class": "concurrent_log_handler.ConcurrentRotatingFileHandler",
                "filename": os.path.join(settings.LOG_PATH, "celery/errors.log"),
                "formatter": "json",
                "encoding": "utf-8",
                "maxBytes": config.LOGGING_MAX_BYTES,
                "backupCount": config.LOGGING_BACKUP_COUNT,
            },
            "info": {
                "level": "INFO",
                "class": "concurrent_log_handler.ConcurrentRotatingFileHandler",
                "filename": os.path.join(settings.LOG_PATH, "celery/info.log"),
                "formatter": "json",
                "encoding": "utf-8",
                "maxBytes": config.LOGGING_MAX_BYTES,
                "backupCount": config.LOGGING_BACKUP_COUNT,
            },
            "console": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "standard",
            },
        },
        "loggers": {
            "celery": {
                "handlers": ["info", "errors"],
                "level": "INFO",
                "propagate": False,
            }
        },
        "root": {"handlers": ["console"], "level": "INFO"},
    }

    logging.config.dictConfig(config_)
