import os

PROD = bool(int(os.getenv("PROD", 0)))

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL")
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

if PROD:
    # NOTE:
    # In general, it feels like better practice to
    # disable celery result backend.
    # Especially, when logging setup is good,
    # storing results looks overkill.
    # If result backend is needed anyway,
    # consider not using DB backend,
    # because it is potentially a lot of extra load on it.
    CELERY_RESULT_BACKEND = None
else:
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND")

CELERY_RESULT_EXTENDED = True
CELERY_TASK_RESULT_EXPIRES = os.environ.get("CELERY_TASK_RESULT_EXPIRES", 30 * 86400)

CELERY_TIMEZONE = "Europe/Moscow"
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_SEND_SENT_EVENT = True
CELERY_WORKER_SEND_TASK_EVENTS = True
CELERY_WORKER_MAX_TASKS_PER_CHILD = 25
CELERYD_TIME_LIMIT = 60

# seems like no point to use django_celery_beat,
# since all scheduled tasks are hardcoded and can not be changed externally
CELERY_BEAT_SCHEDULER = "celery.beat:PersistentScheduler"
CELERY_BEAT_SCHEDULE = {}
CELERY_BEAT_MAX_LOOP_INTERVAL = 5 * 60  # in seconds
