from .base import *

SECRET_KEY = "foo"

STORAGES["default"]["BACKEND"] = "django.core.files.storage.InMemoryStorage"
MEDIA_ROOT = "/"
PNGCRUSH_CMD = None
