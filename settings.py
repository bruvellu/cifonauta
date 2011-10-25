# -*- coding: utf-8 -*-

# Django settings for weblarvae project.

import os
import socket

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
        'default': {
            'NAME': '',
            'ENGINE': '',
            'USER': '',
            }
        }

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Sao_Paulo'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
#XXX Tem que ser minúscula para evitar problema com datatrans
LANGUAGE_CODE = 'pt-br'
ADMIN_LANGUAGE_CODE = 'pt-br'

ugettext = lambda s: s
# Línguas disponíveis.
LANGUAGES = (
    ('pt-br', ugettext('Português')),
    ('en', ugettext('English')),
)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_DIR, 'site_media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/site_media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'
#ADMIN_MEDIA_PREFIX = '/site_media/admin/media/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
        ('django.template.loaders.cached.Loader', (
            #'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
            )),
        #'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
        'johnny.middleware.LocalStoreClearMiddleware',
        'johnny.middleware.QueryCacheMiddleware',
        'django.middleware.cache.UpdateCacheMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.middleware.locale.LocaleMiddleware',
        'utils.AdminLocaleURLMiddleware',
        'debug_toolbar.middleware.DebugToolbarMiddleware',
        'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.middleware.transaction.TransactionMiddleware',
        'django.middleware.cache.FetchFromCacheMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    )

# Required for Debug Toolbar and sorl-thumbnail.
INTERNAL_IPS = ('127.0.0.1',)

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    }

# Dajaxice requirement.
DAJAXICE_MEDIA_PREFIX = 'dajaxice'

ROOT_URLCONF = 'weblarvae.urls'

TEMPLATE_DIRS = (
        #os.path.join(PROJECT_DIR, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.flatpages',
    'django.contrib.humanize',
    'django.contrib.markup',
    'django.contrib.syndication',
    'meta',
    'articles',
    'south',
    'mptt',
    'rosetta',
    'datatrans',
    'debug_toolbar',
    'sorl.thumbnail',
    'dajaxice',
    'dajax',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[%(levelname)s] %(asctime)s @ %(module)s %(funcName)s (l%(lineno)d): %(message)s'
            }
        },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'default'
        },
        'log_files': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(PROJECT_DIR, 'logs/central.log'),
            'formatter': 'default'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'central': {
            'handlers': ['log_files', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}


# Logicamente carrega configurações.
if socket.gethostname() == 'cifonauta':
    # Importa dados para servidor.
    from settings_server import *
else:
    # Importa dados para desenvolvimento.
    from settings_local import *
