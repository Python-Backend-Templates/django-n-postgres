""" Project constants and configuration """

import os
from typing import List

LOGGING_LOGGERS: List[str] = os.environ.get("LOGGING_LOGGERS", "").split(",")
LOGGING_SENSITIVE_FIELDS: List[str] = os.environ.get(
    "LOGGING_SENSITIVE_FIELDS", ""
).split(",")
LOGGING_MAX_BYTES: int = int(os.environ.get("LOGGING_MAX_BYTES", 1024 * 8))
LOGGING_BACKUP_COUNT: int = int(os.environ.get("LOGGING_MAX_BYTES", 3))
