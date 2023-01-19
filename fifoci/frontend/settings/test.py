from .base import *

DEBUG = True
TEMPLATE_DEBUG = True

SECRET_KEY = "foo"

INSTALLED_APPS = INSTALLED_APPS + ("debug_toolbar",)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "fifoci",
        "USER": "fifoci",
        "HOST": "fifoci.dolphin-emu.org",
        "PORT": 6000,
    }
}
