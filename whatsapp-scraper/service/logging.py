import logging

from celery import current_task


class TaskNameFilter(logging.Filter):
    def filter(self, record):
        task_name = getattr(current_task, "name", None)
        if task_name:
            record.task_name = task_name
        else:
            record.task_name = "unknown_task"
        return True


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
        "task_simple": {
            "format": "{levelname} [{asctime}] [{task_name}] {message}",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "style": "{",
        },
    },
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
        "task_name_filter": {
            "()": "service.logging.TaskNameFilter",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "filters": [],
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "console_task": {
            "level": "INFO",
            "filters": ["task_name_filter"],
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
            "filters": ["task_name_filter"],
            "class": "logging.handlers.TimedRotatingFileHandler",
            "when": "midnight",  # Rotate logs at midnight
            "interval": 1,  # Rotate logs every day
            "backupCount": 7,  # Keep 7 days of logs
            "filename": "logs/scraper.log",
            "formatter": "simple",
        },
        "practice_hub_handler": {
            "level": "INFO",
            "filters": ["task_name_filter"],
            "class": "logging.handlers.TimedRotatingFileHandler",
            "when": "midnight",  # Rotate logs at midnight
            "interval": 1,  # Rotate logs every day
            "backupCount": 7,  # Keep 7 days of logs
            "filename": "logs/practice_hub.log",
            "formatter": "simple",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "django"],
            "propagate": True,
        },
        "scraper": {
            "handlers": ["console_task", "file_scraper"],
            "level": "INFO",
            "propagate": False,
        },
        "practice_hub": {
            "handlers": ["console_task", "practice_hub_handler"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
