# Django settings for weblarvae project.

# Preencha os settings necessários e renomeie para settings_local.py

import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG
THUMBNAIL_DEBUG = DEBUG


ADMINS = (
    ('Nome', 'Email'),
)

MANAGERS = ADMINS

# Banco de dados local para desenvolvimento.
DATABASES = {
        'default': {
            'NAME': '',
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'USER': '',
            'OPTIONS': {
                'autocommit': True,
                }
            }
        }

CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
            'LOCATION': '',
            'TIMEOUT': 3600,
            'OPTIONS': {
                'MAX_ENTRIES': 100000,
                }
            },
        'johnny': {
            'BACKEND': 'johnny.backends.memcached.MemcachedCache',
            'LOCATION': '127.0.0.1:11211',
            'JOHNNY_CACHE': False,
            }
        }

JOHNNY_MIDDLEWARE_KEY_PREFIX = 'jc_cifo'
DISABLE_QUERYSET_CACHE = True

CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 3600
CACHE_MIDDLEWARE_KEY_PREFIX = 'cifo'
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''
