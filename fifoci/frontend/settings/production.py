import os

from .base import *

if "SECRET_KEY_FILE" in os.environ:
    SECRET_KEY = open(os.environ["SECRET_KEY_FILE"]).read()

if "STATIC_ROOT" in os.environ:
    STATIC_ROOT = os.environ["STATIC_ROOT"]

if "MEDIA_ROOT" in os.environ:
    MEDIA_ROOT = os.environ["MEDIA_ROOT"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ.get("POSTGRES_DB", "fifoci"),
        "USER": os.environ.get("POSTGRES_USER", "fifoci"),
    }
}
