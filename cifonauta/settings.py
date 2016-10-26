# -*- coding: utf-8 -*-
"""
Django settings for cifonauta project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import socket
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Dummy security settings.
SECRET_KEY = 'o3d^5p6yf($kcg=j*&%+-a3+j4(unk4uutgqnzsk^yy)=ggqv%'
DEBUG = True
TEMPLATE_DEBUG = True
THUMBNAIL_DEBUG = True
ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = (
    'modeltranslation', # Before admin.
    'django.contrib.flatpages',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'haystack',

    'meta',
    'mptt',
    'rosetta',
    'sorl.thumbnail',

    'django.contrib.sites',
    'django.contrib.humanize',
    'django.contrib.syndication',
    'django.contrib.sitemaps',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'django.middleware.locale.LocaleMiddleware',
    'utils.AdminLocaleURLMiddleware',

    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
)

ROOT_URLCONF = 'cifonauta.urls'
WSGI_APPLICATION = 'cifonauta.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'cebimar',
        'USER': 'nelas',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/
LANGUAGE_CODE = 'pt-br'
ADMIN_LANGUAGE_CODE = 'pt-br'

# Rosetta settings.
ROSETTA_MESSAGES_SOURCE_LANGUAGE_CODE = 'pt-br'
ROSETTA_MESSAGES_SOURCE_LANGUAGE_NAME = 'Português'
ROSETTA_STORAGE_CLASS = 'rosetta.storage.CacheRosettaStorage'

TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_L10N = True
USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

# Needed for modeltranslation.
ugettext = lambda s: s
LANGUAGES = (
   ('pt-br', ugettext('Português')),
   ('en', ugettext('English')),
)
MODELTRANSLATION_DEFAULT_LANGUAGE = 'pt-br'
MODELTRANSLATION_FALLBACK_LANGUAGES = ('pt-br', 'en')
MODELTRANSLATION_AUTO_POPULATE = True

# Needed for Django sites framework. Keep it active.
SITE_ID = 1

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'site_media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/site_media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.request",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages"
)

# Required for sorl-thumbnail.
INTERNAL_IPS = ('127.0.0.1', '::1')

# Elasticsearch
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'haystack',
        },
}

import logging
from sorl.thumbnail.log import ThumbnailLogHandler
handler = ThumbnailLogHandler()
handler.setLevel(logging.ERROR)
logging.getLogger('sorl.thumbnail').addHandler(handler)

# Logging.
#LOGGING_CONFIG = None

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
#LOGGING = {
#    'version': 1,
#    'disable_existing_loggers': False,
#    'formatters': {
#        'default': {
#            'format': '[%(levelname)s] %(asctime)s @ %(module)s %(funcName)s (l%(lineno)d): %(message)s'
#            }
#        },
#    'handlers': {
#        'mail_admins': {
#            'level': 'ERROR',
#            'class': 'django.utils.log.AdminEmailHandler'
#        },
#        'console':{
#            'level':'DEBUG',
#            'class':'logging.StreamHandler',
#            'formatter': 'default'
#        },
#        'log_files': {
#            'level': 'DEBUG',
#            'class': 'logging.FileHandler',
#            'filename': os.path.join(BASE_DIR, 'logs/central.log'),
#            'formatter': 'default'
#        }
#    },
#    'loggers': {
#        'django.request': {
#            'handlers': ['mail_admins'],
#            'level': 'ERROR',
#            'propagate': True,
#        },
#        'central': {
#            'handlers': ['log_files', 'console'],
#            'level': 'DEBUG',
#            'propagate': False,
#        },
#    }
#}

#CACHES = {
        #'default': {
            #'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
            #'LOCATION': '',
            #'TIMEOUT': 3600,
            #'OPTIONS': {
                #'MAX_ENTRIES': 100000,
                #}
            #},
        #'johnny': {
            #'BACKEND': 'johnny.backends.memcached.MemcachedCache',
            #'LOCATION': '127.0.0.1:11211',
            #'JOHNNY_CACHE': False,
            #}
        #}

#JOHNNY_MIDDLEWARE_KEY_PREFIX = 'jc_cifo'
#DISABLE_QUERYSET_CACHE = True

#CACHE_MIDDLEWARE_ALIAS = 'default'
#CACHE_MIDDLEWARE_SECONDS = 3600
#CACHE_MIDDLEWARE_KEY_PREFIX = 'cifo'
#CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True

# Storage folder.
STORAGE_FOLDER = '/home/nelas/storage/oficial'

# Import server settings.
hostname = socket.gethostname()
if hostname == 'cifonauta' or hostname == 'cebimar-002':
    from server_settings import *
