"""
Django settings for service project.

Generated by 'django-admin startproject' using Django 5.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path

import environ
from django.contrib.messages import constants as messages

from .logging import LOGGING  # noqa

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, True)
)

ENV_DEV = "dev"
ENV_QA = "qa"
ENV_PROD = "prod"
ENVIRONMENT_FLAVOR = env.str("ENVIRONMENT_FLAVOR", default=ENV_DEV)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str(
    "DJANGO_SECRET_KEY", default="h6*smaj5a88z*y1f+o=rn%8t798z3*b5342_r&dk+0q_(6l@hg"
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=True)

ALLOWED_HOSTS = [env.str("ALLOWED_HOSTS", default="127.0.0.1")]

# CORS_ORIGIN_ALLOW_ALL = True
# CORS_ALLOW_CREDENTIALS = True

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "simple_history",
    "django_celery_beat",
    "solo",
    "whatsapp_scraper",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
]

DEBUG_TOOLBAR_ENABLED = env.bool("DEBUG_TOOLBAR_ENABLED", default=False)
if DEBUG_TOOLBAR_ENABLED:
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": lambda request: True,
        # Toolbar options
        "RESULTS_CACHE_SIZE": 3,
        "SHOW_COLLAPSED": True,
        # Panel options
        "SQL_WARNING_THRESHOLD": 100,  # milliseconds
    }

ROOT_URLCONF = "service.urls"

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

WSGI_APPLICATION = "service.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env.str("DATABASE", default="whatsappscraperdb"),
        "USER": env.str("USERNAME", default="admin"),
        "PASSWORD": env.str("PASSWORD", default="admin"),
        "HOST": env.str("HOST", default="127.0.0.1"),
        "PORT": env.int("PORT", default=5432),
    }
}
# REDIS_URL = env.str('REDIS_URL', default='redis://redis:6379/1')

# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': REDIS_URL,
#         'OPTIONS': {
#             'CLIENT_CLASS': 'django_redis.client.DefaultClient'
#         },
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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

MESSAGE_TAGS = {
    messages.DEBUG: "alert-info",
    messages.INFO: "alert-info",
    messages.SUCCESS: "alert-success",
    messages.WARNING: "alert-warning",
    messages.ERROR: "alert-danger",
}


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_ROOT = "static"
STATIC_URL = "/static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ------------ Celery
APP_VHOST = env.str("APP_VHOST", default="whatsapp-scraper")
CELERY_BROKER_URL = env.str(
    "CELERY_BROKER_URL", f"pyamqp://rabbitmq:rabbitmq@rabbitmq:5672/{APP_VHOST}"
)
# CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"
CELERY_ENABLE_UTC = True
CELERY_ALWAYS_EAGER = env.bool("DJ_CELERY_TASK_ALWAYS_EAGER", default=False)
CELERY_TASK_ALWAYS_EAGER = env.bool("DJ_CELERY_TASK_ALWAYS_EAGER", default=False)
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERYBEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_IGNORE_RESULT = True
CELERY_DEFAULT_QUEUE = "default"
CELERYD_PREFETCH_MULTIPLIER = 1
CELERY_ACKS_LATE = True

PROXY_ACTIVE = env.bool("PROXY_ACTIVE", default=False)
HEADLESS = env.bool("HEADLESS", default=True)
BROWSER = env.str("BROWSER", default="chrome")
CONNECTION_TYPE = env.str("CONNECTION_TYPE", default="remote")
WEB_DRIVER_PATH = env.str("WEB_DRIVER_PATH", default="/chromedriver")
WEB_DRIVER_URL = env.str("WEB_DRIVER_URL", default="")
LOGIN_WEB_DRIVER_URL = env.str("LOGIN_WEB_DRIVER_URL", default="")
DOCKER_MANAGER_SERVICE_PORT = env.int("DOCKER_MANAGER_SERVICE_PORT", default=5000)

USER_DATA_DIR_BASE_FOLDER = f"{BASE_DIR.parent}/seluser-data-dir"

PRACTICE_HUB_ACCOUNT_DOMAIN = env.str("PRACTICE_HUB_ACCOUNT_DOMAIN", default="")
PRACTICE_HUB_API_KEY = env.str("PRACTICE_HUB_API_KEY", default="")
PRACTICE_HUB_CONTACT_EMAIL = env.str("PRACTICE_HUB_CONTACT_EMAIL", default="")