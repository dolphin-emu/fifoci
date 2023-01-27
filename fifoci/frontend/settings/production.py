import os

from .base import *

DEBUG = TEMPLATE_DEBUG = False

if "SECRET_KEY_FILE" in os.environ:
    SECRET_KEY = open(os.environ["SECRET_KEY_FILE"]).read()

if "IMPORT_API_KEY_FILE" in os.environ:
    IMPORT_API_KEY = open(os.environ["IMPORT_API_KEY_FILE"]).read()

if "STATIC_ROOT" in os.environ:
    STATIC_ROOT = os.environ["STATIC_ROOT"]

if "MEDIA_ROOT" in os.environ:
    MEDIA_ROOT = os.environ["MEDIA_ROOT"]

if "ALLOWED_HOSTS" in os.environ:
    ALLOWED_HOSTS = os.environ["ALLOWED_HOSTS"].split(",")
    CSRF_TRUSTED_ORIGINS = [
        "https://" + h for h in os.environ["ALLOWED_HOSTS"].split(",")
    ]

if "PNGCRUSH_CHD" in os.environ:
    PNGCRUSH_CMD = os.environ["PNGCRUSH_CMD"]

# Always log to stdout.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ.get("POSTGRES_DB", "fifoci"),
        "USER": os.environ.get("POSTGRES_USER", "fifoci"),
    }
}

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
