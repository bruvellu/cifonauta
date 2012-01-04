# Django settings for weblarvae project.

# Preencha os settings necessários e renomeie para settings_server.py

import os

DEBUG = False
TEMPLATE_DEBUG = DEBUG
THUMBNAIL_DEBUG = DEBUG


ADMINS = (
    ('Nome', 'Email'),
)

MANAGERS = ADMINS

# Banco de dados local para desenvolvimento.
DATABASES = {
        'default': {
            'HOST': '',
            'PORT': '',
            'NAME': '',
            'ENGINE': '',
            'USER': '',
            'OPTIONS': {
                'autocommit': True,
                }
            }
        }


CACHES = {
        'default': {
            'BACKEND': '',
            'LOCATION': '',
            'TIMEOUT': 3600,
            'OPTIONS': {
                'MAX_ENTRIES': 1000,
                }
            },
        'johnny': {
            'BACKEND': '',
            'LOCATION': '',
            'JOHNNY_CACHE': True,
            }
        }

JOHNNY_MIDDLEWARE_KEY_PREFIX = 'jc_cifo'
#DISABLE_QUERYSET_CACHE = True

CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 3600
CACHE_MIDDLEWARE_KEY_PREFIX = 'cifo'
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True


# Make this unique, and don't share it with anybody.
SECRET_KEY = ''
