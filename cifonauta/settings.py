# -*- coding: utf-8 -*-
"""
Django settings for cifonauta project.

Generated by 'django-admin startproject' using Django 2.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import socket

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Dummy (!) settings. Production values are in server/server_settings.py
SECRET_KEY = 'o3d^5p6yf($kcg=j*&%+-a3+j4(unk4uutgqnzsk^yy)=ggqv%'
DEBUG = True
THUMBNAIL_DEBUG = True
ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'modeltranslation', # Before admin.
    'django.contrib.flatpages',

    'meta.apps.MetaConfig',
    'model_translator',
    'mptt',
    'rosetta',
    'sorl.thumbnail',
    'debug_toolbar',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',

    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.humanize',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
]

ROOT_URLCONF = 'cifonauta.urls'

TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.template.context_processors.i18n',
                    'django.template.context_processors.media',
                    'django.template.context_processors.static',
                    'django.template.context_processors.tz',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                    ],
                'builtins': [
                    'meta.templatetags.extra_tags',
                    ],
                },
            },
        ]

WSGI_APPLICATION = 'cifonauta.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'cebimar',
        'USER': 'nelas',
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'pt-br'
ADMIN_LANGUAGE_CODE = 'pt-br'

# Rosetta settings.
ROSETTA_MESSAGES_SOURCE_LANGUAGE_CODE = 'pt-br'
ROSETTA_MESSAGES_SOURCE_LANGUAGE_NAME = 'Português'
ROSETTA_STORAGE_CLASS = 'rosetta.storage.CacheRosettaStorage'

# Time zones
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Needed for modeltranslation.
ugettext = lambda s: s
LANGUAGES = (
   ('pt-br', ugettext('Português')),
   ('en', ugettext('English')),
)
MODELTRANSLATION_DEFAULT_LANGUAGE = 'pt-br'
MODELTRANSLATION_FALLBACK_LANGUAGES = ('pt-br', 'en')
MODELTRANSLATION_AUTO_POPULATE = True

# Set default value for AutoField
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Needed for Django sites framework. Keep it active.
SITE_ID = 1

# Absolute path to the directory that holds site media.
MEDIA_ROOT = os.path.join(BASE_DIR, 'site_media')

# Absolute path to the directory that holds source media.
SOURCE_ROOT = os.path.join(BASE_DIR, 'source_media')

# List of accepted file extensions.
PHOTO_EXTENSIONS = ('tif', 'tiff', 'jpg', 'jpeg', 'png', 'gif')
VIDEO_EXTENSIONS = ('avi', 'mov', 'mp4', 'ogv', 'dv', 'mpg', 'mpeg', 'flv', 'm2ts', 'wmv')
MEDIA_EXTENSIONS = PHOTO_EXTENSIONS + VIDEO_EXTENSIONS

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/site_media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Increase limit for fields
DATA_UPLOAD_MAX_NUMBER_FIELDS = 15000

# Required for debug_toolbar
INTERNAL_IPS = ['127.0.0.1']

#import logging
#from sorl.thumbnail.log import ThumbnailLogHandler
#handler = ThumbnailLogHandler()
#handler.setLevel(logging.ERROR)
#logging.getLogger('sorl.thumbnail').addHandler(handler)

# Import server settings.
hostname = socket.gethostname()
if hostname == 'cifonauta':
    from .server_settings import *
