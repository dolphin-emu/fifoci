from fifoci.settings.base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'fifoci',
        'USER': 'fifoci',
    }
}
