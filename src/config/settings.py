import os
import sys
from pathlib import Path


from utils.logging import get_config

from .celery_config import *  # noqa: F401,F403


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = bool(int(os.environ.get("DEBUG", 0)))
PROD = bool(int(os.environ.get("PROD", 1)))
TESTING = "pytest" in sys.modules
IN_CELERY_WORKER = sys.argv and sys.argv[0].endswith("celery") and "worker" in sys.argv

ALLOWED_HOSTS = [
    "0.0.0.0",
    "127.0.0.1",
    "localhost",
]
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000/"
]

USE_X_FORWARDED_HOST = True  # !!! Only behind proxy !!!
SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)  # !!! Only behind proxy !!!


# Application definition

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    # third party
    "rest_framework",
    "drf_spectacular",
    "django_celery_results",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "utils.middleware.ShowSQLMiddleware",
    "utils.middleware.LogRequestMiddleware",
]

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    # "DEFAULT_AUTHENTICATION_CLASSES": ("TODO",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "utils.exceptions.custom_exception_handler",
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.NamespaceVersioning",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "API",
    "DESCRIPTION": "Release 0.0.1",
    "VERSION": "0.0.1",
    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_SETTINGS": {
        "filter": True,
    },
    "COMPONENT_SPLIT_REQUEST": True,
    "DISABLE_ERRORS_AND_WARNINGS": True,
    "SCHEMA_PATH_PREFIX": r"/api/v[0-9]",
    "PREPROCESSING_HOOKS": [],
}


ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME"),
        "USER": os.environ.get("DB_USER"),
        "PASSWORD": os.environ.get("DB_PASSWORD"),
        "HOST": os.environ.get("DB_HOST"),
        "PORT": os.environ.get("DB_PORT"),
        "CONN_MAX_AGE": 5,
        "TEST": {
            "NAME": "test_database",
        },
    }
}


CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"redis://{os.environ.get('REDIS_HOST')}:{os.environ.get('REDIS_PORT')}/0",  # noqa: E501
    },
}


# AUTH_USER_MODEL = "TODO"
# AUTHENTICATION_BACKENDS = ["TODO"]
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

STATIC_URL = os.environ.get("STATIC_URL")
STATIC_ROOT = "/static/"

MEDIA_URL = os.environ.get("MEDIA_URL")
MEDIA_ROOT = "/media/"

LOG_PATH = "/logs/"
LOGGING = get_config(LOG_PATH)
