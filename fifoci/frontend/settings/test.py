from .base import *

SECRET_KEY = "foo"

STORAGES["default"]["BACKEND"] = "inmemorystorage.InMemoryStorage"
MEDIA_ROOT = "/"
PNGCRUSH_CMD = None
