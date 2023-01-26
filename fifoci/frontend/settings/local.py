from .base import *

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "db.sqlite3",
    }
}

DEBUG = True
TEMPLATE_DEBUG = True

INSTALLED_APPS = INSTALLED_APPS + ("debug_toolbar",)
MIDDLEWARE = MIDDLEWARE + ("debug_toolbar.middleware.DebugToolbarMiddleware",)

ALLOWED_HOSTS = ALLOWED_HOSTS + ["localhost", "127.0.0.1"]
INTERNAL_IPS = ["127.0.0.1"]
