import os
from pathlib import Path
from typing import Dict

from json_log_formatter import VerboseJSONFormatter, _json_serializable

from config import config


class JsonLogFormatter(VerboseJSONFormatter):
    def to_json(self, record):
        try:
            return self.json_lib.dumps(
                record, default=_json_serializable, ensure_ascii=False
            )
        # ujson doesn't support default argument and raises TypeError.
        # "ValueError: Circular reference detected" is raised
        # when there is a reference to object inside the object itself.
        except (TypeError, ValueError, OverflowError):
            try:
                return self.json_lib.dumps(record, ensure_ascii=False)
            except (TypeError, ValueError, OverflowError):
                return "{}"

    def extra_from_record(self, record) -> Dict:
        return {"extra": self.sensitive_data_filter(super().extra_from_record(record))}

    def sensitive_data_filter(self, data: Dict) -> Dict:
        def _filter_dict(data: Dict):
            new_data = {}
            for k, v in data.items():
                if k.lower() not in config.LOGGING_SENSITIVE_FIELDS:
                    if isinstance(v, dict):
                        new_data[k] = _filter_dict(v)
                    else:
                        new_data[k] = v

            return new_data

        return _filter_dict(data)


def get_config(log_path: str) -> Dict:
    default_hanlder_settings = {
        "class": "concurrent_log_handler.ConcurrentRotatingFileHandler",
        "encoding": "utf-8",
        "maxBytes": config.LOGGING_MAX_BYTES,
        "backupCount": config.LOGGING_BACKUP_COUNT,
    }
    handlers = {}
    loggers = {}
    for logger_name in config.LOGGING_LOGGERS:
        try:
            Path(log_path + logger_name).mkdir(parents=False, exist_ok=True)
        except (FileExistsError, FileNotFoundError):
            pass

        handlers[f"{logger_name}-info"] = {
            "level": "INFO",
            "filename": os.path.join(log_path, f"{logger_name}/info.log"),
            "formatter": "json",
            **default_hanlder_settings,
        }
        handlers[f"{logger_name}-errors"] = {
            "level": "ERROR",
            "filename": os.path.join(log_path, f"{logger_name}/errors.log"),
            "formatter": "json",
            **default_hanlder_settings,
        }
        loggers[logger_name] = {
            "handlers": [f"{logger_name}-info", f"{logger_name}-errors"],
            "level": "INFO",
            "propagate": False,
        }

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": "utils.logging.JsonLogFormatter",
            },
            "verbose": {
                "format": "[{asctime}] [{module}] [{funcName}] [{levelname}] {message}",
                "style": "{",
            },
            "standard": {
                "format": "{levelname} {asctime}: {message}",
                "style": "{",
            },
        },
        "handlers": {
            **handlers,
            "console": {
                "formatter": "verbose",
                "class": "logging.StreamHandler",
            },
            "errors": {
                "level": "ERROR",
                "filename": os.path.join(log_path, "errors.log"),
                "formatter": "json",
                **default_hanlder_settings,
            },
            "default": {
                "level": "INFO",
                "filename": os.path.join(log_path, "info.log"),
                "formatter": "json",
                **default_hanlder_settings,
            },
        },
        "loggers": {
            **loggers,
            "": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }
