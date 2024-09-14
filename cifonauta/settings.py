# -*- coding: utf-8 -*-
"""
Django settings for the Cifonauta project.
"""

import os
import socket

from dotenv import load_dotenv
load_dotenv()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Dummy settings
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
    'user',

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

    'rest_framework',
    'captcha',
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
            'APP_DIRS': True,
            'DIRS': [],
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
        'USER': 'nelas'
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

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

# Time zones
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Needed for modeltranslation
gettext = lambda s: s
LANGUAGES = [('pt-br', gettext('Português')),
             ('en', gettext('English')),]
MODELTRANSLATION_DEFAULT_LANGUAGE = 'pt-br'
MODELTRANSLATION_FALLBACK_LANGUAGES = ('pt-br', 'en')
MODELTRANSLATION_AUTO_POPULATE = False

# Rosetta settings
ROSETTA_MESSAGES_SOURCE_LANGUAGE_CODE = 'pt-br'
ROSETTA_MESSAGES_SOURCE_LANGUAGE_NAME = 'Português'
ROSETTA_STORAGE_CLASS = 'rosetta.storage.CacheRosettaStorage'
ROSETTA_SHOW_AT_ADMIN_PANEL = True

# Set default value for AutoField
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Needed for Django sites framework
SITE_ID = 1

# Absolute path to the directory that holds site media
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# Defines subdirectory of MEDIA_ROOT to store user uploads
UPLOAD_ROOT = 'uploads'

# [deprecated] Absolute path to the directory that holds source media.
SOURCE_ROOT = os.path.join(BASE_DIR, 'source_media')

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'meta/static'),
    os.path.join(BASE_DIR, 'user/static'),
    # Add other app directories if necessary
]

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
ADMIN_MEDIA_PREFIX = '/static/admin/'

# List of accepted file extensions.
#TODO: Increase accepted extensions?
# PHOTO_EXTENSIONS = ('tif', 'tiff', 'jpg', 'jpeg', 'png', 'gif')
# VIDEO_EXTENSIONS = ('avi', 'mov', 'mp4', 'ogv', 'dv', 'mpg', 'mpeg', 'flv', 'm2ts', 'wmv')
#TODO: Remove dots
PHOTO_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif',)
VIDEO_EXTENSIONS = ('.mp4',)
MEDIA_EXTENSIONS = PHOTO_EXTENSIONS + VIDEO_EXTENSIONS

# List of accepted file mime types
IMAGE_MIMETYPES = ('image/jpeg', 'image/png',)
VIDEO_MIMETYPES = ('video/mp4',)
MEDIA_MIMETYPES = IMAGE_MIMETYPES + VIDEO_MIMETYPES

# Size limits for images (3MB) and videos (1GB)
IMAGE_SIZE_LIMIT = 3 * 1024 * 1024
VIDEO_SIZE_LIMIT = 1 * 1024 * 1024 * 1024

# Default dimensions and quality for different media files
# Image quality in percentage (0-100%)
# Video quality in bitrate (0-infinite kbits/s)
MEDIA_DEFAULTS = {
        'photo': {
            'extension': 'jpg',
            'large': {'dimension': 2000, 'quality': 90},
            'medium': {'dimension': 1000, 'quality': 70},
            'small': {'dimension': 500, 'quality': 70},
            'cover': {'dimension': 750, 'quality': 70}
            },
        'video': {
            'extension': 'mp4',
            'large': {'dimension': 1920, 'quality': 2000},
            'medium': {'dimension': 1280, 'quality': 1000},
            'small': {'dimension': 640, 'quality': 600},
            'cover': {'dimension': 750, 'quality': 70}
            },
        }

# Regex for filename of uploaded files
FILENAME_REGEX = fr'{os.environ["FILENAME_REGEX"]}'

# Increase limit for fields
DATA_UPLOAD_MAX_NUMBER_FIELDS = 15000

# Required for debug_toolbar
INTERNAL_IPS = ['127.0.0.1']
RESULTS_CACHE_SIZE = 100000

# Custom user model
AUTH_USER_MODEL = 'user.UserCifonauta'

#TODO: Document
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

# Location of captcha database
CAPTCHA_STORE = 'captcha.store.database.DatabaseStore'

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
EMAIL_USE_TLS = True

# Import server settings.
hostname = socket.gethostname()
if hostname == 'cifonauta':
    from .server_settings import *


