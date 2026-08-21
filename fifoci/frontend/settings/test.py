from .base import *

DEBUG = True
TEMPLATE_DEBUG = True

SECRET_KEY = "foo"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "fifoci",
        "USER": "fifoci",
        "HOST": "fifoci.dolphin-emu.org",
        "PORT": 6000,
    }
}
