LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} [{asctime}] {message}",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "style": "{",
        },
    },
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "filters": [],
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "django": {
            "level": "INFO",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "when": "midnight",  # Rotate logs at midnight
            "interval": 1,  # Rotate logs every day
            "backupCount": 7,  # Keep 7 days of logs
            "filename": "logs/django.log",
            "formatter": "simple",
        },
        "file_scraper": {
            "level": "INFO",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "when": "midnight",  # Rotate logs at midnight
            "interval": 1,  # Rotate logs every day
            "backupCount": 7,  # Keep 7 days of logs
            "filename": "logs/scraper.log",
            "formatter": "simple",
        },
        "tasks_handler": {
            "level": "INFO",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "when": "midnight",  # Rotate logs at midnight
            "interval": 1,  # Rotate logs every day
            "backupCount": 7,  # Keep 7 days of logs
            "filename": "logs/tasks.log",
            "formatter": "simple",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "django"],
            "propagate": True,
        },
        "scraper": {
            "handlers": ["console", "file_scraper"],
            "level": "INFO",
            "propagate": False,
        },
        "tasks": {
            "handlers": ["console", "tasks_handler"],
            "level": "INFO",
            "propagate": False,
        },
    },
}