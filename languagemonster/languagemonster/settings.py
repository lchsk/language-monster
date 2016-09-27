from __future__ import absolute_import

import logging
import sys
import os
from logging.handlers import RotatingFileHandler

ID = 'languagemonster'
VERSION = '0.1.0'
BRANCH = 'master'

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('LM_SECRET_KEY', '123456789')
API_KEY = os.getenv('LM_API_KEY')
GAME_SESSION_KEY = os.getenv('LM_GAME_SESSION_KEY')

CACHE_SECONDS = 600
CACHE = False

FORCE_DB_DEBUG = os.environ.get('FORCE_DB_DEBUG', False)

if len(sys.argv) >= 2:
    DEBUG = (sys.argv[1] == 'runserver')
else:
    DEBUG = False

DEBUG_GAMES = DEBUG
THUMBNAIL_DEBUG = DEBUG
PROFILING_SQL_QUERIES = DEBUG

# Loggin configuration

LOG_FORMATTER = logging.Formatter(
    '%(asctime)s %(levelname)s %(name)s %(funcName)s(%(lineno)d) %(message)s'
)

LOG_DIR = os.getenv('LM_LOG_DIR', './')
LOG_WWW_FILE = LOG_DIR + 'www.log'
LOG_API_FILE = LOG_DIR + 'api.log'
LOG_WORKERS_FILE = LOG_DIR + 'workers.log'
LOG_MAIL_FILE = LOG_DIR + 'mail.log'

# 20M
LOG_FILE_SIZE = 20 * 1000 * 1000

LOG_WWW_HANDLER = RotatingFileHandler(
    LOG_WWW_FILE,
    mode = 'a',
    maxBytes = LOG_FILE_SIZE,
    backupCount = 20,
    encoding = None,
    delay = 0
)

LOG_API_HANDLER = RotatingFileHandler(
    LOG_API_FILE,
    mode = 'a',
    maxBytes = LOG_FILE_SIZE,
    backupCount = 20,
    encoding = None,
    delay = 0
)

LOG_WORKERS_HANDLER = RotatingFileHandler(
    LOG_WORKERS_FILE,
    mode = 'a',
    maxBytes = LOG_FILE_SIZE,
    backupCount = 20,
    encoding = None,
    delay = 0
)

LOG_MAIL_HANDLER = RotatingFileHandler(
    LOG_MAIL_FILE,
    mode = 'a',
    maxBytes = LOG_FILE_SIZE,
    backupCount = 20,
    encoding = None,
    delay = 0
)

LOG_PRODUCTION_LEVEL = logging.INFO

def LOGGER(logger, handler = LOG_WWW_HANDLER):
    """
        Function for setting logging in other modules.
    """

    handler.setFormatter(LOG_FORMATTER)

    if DEBUG:
        handler.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    else:
        handler.setLevel(LOG_PRODUCTION_LEVEL)
        logger.setLevel(LOG_PRODUCTION_LEVEL)

    logger.addHandler(handler)

######################

ALLOWED_HOSTS = os.getenv('LM_ALLOWED_HOSTS', '').split(',')
LOCAL_API_HOSTS = ('127.0.0.1',)

REDIS_HOST = os.getenv('LM_REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('LM_REDIS_PORT', '1234')

MONSTER_URL = os.getenv('LM_MONSTER_URL', '/')

THUMBNAIL_FORMAT = 'PNG'
THUMBNAIL_KVSTORE = 'sorl.thumbnail.kvstores.redis_kvstore.KVStore'
THUMBNAIL_REDIS_HOST = REDIS_HOST
THUMBNAIL_REDIS_PORT = REDIS_PORT
THUMBANIL_ENGINE = 'sorl.thumbnail.engines.pil_engine.Engine'

#####################
# Games configuration
#####################
from django.utils.translation import ugettext_lazy as _

GAMES_USE_CANVAS_ONLY = False

# Number of word pairs user learns during a game level
GAMES_DEFAULT_WORDS_COUNT = 4 if DEBUG else 8

# Number of word sets returned in a single (default) call
GAMES_DEFAULT_WORD_SETS_COUNT = 10

GAMES = {
    'space': {
        'available' : True,
        'name' : _('game_space_game'),
        'image' : 'space2.png'
    },
    'simple': {
        'available' : True,
        'name' : _('game_four_buttons'),
        'image' : 'simple.png'
    },
    'plane': {
        'available' : True,
        'name' : _('game_crazy_plane'),
        'image' : 'plane.png'
    },
    'runner': {
        'available' : True,
        'name' : _('game_bunny_runner'),
        'image' : 'runner.png'
    },
    'shooter': {
        'available' : True,
        'name' : _('game_word_sniper'),
        'image' : 'shooter.png'
    }
}

# End of games configuration

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'debug_toolbar',
    'sysmon',
    'sorl.thumbnail',
    'rosetta',
    'core',
    'post_office',
    'rest_framework',
    'api',
    'vocabulary',
    'ctasks',
    'userprofile',
    'django_countries',
)

MIDDLEWARE_CLASSES = ()

if CACHE:
    MIDDLEWARE_CLASSES += ('django.middleware.cache.UpdateCacheMiddleware',)

MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',

    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

if CACHE:
    MIDDLEWARE_CLASSES += ('django.middleware.cache.FetchFromCacheMiddleware',)

ROOT_URLCONF = 'languagemonster.urls'

WSGI_APPLICATION = 'languagemonster.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_ROOT, 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

if not DEBUG:
    TEMPLATES[0]['APP_DIRS'] = False
    TEMPLATES[0]['OPTIONS']['loaders'] = [
        ('django.template.loaders.cached.Loader', [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ]),
    ]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    # FIXME:
    # Setting below causes 415 in response...
    # Probably need to list of parser classes...
    # 'DEFAULTl_PARSER_CLASSES': (
    #     'rest_framework.parsers.JSONParser',
    # ),
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('LM_DB_NAME'),
        'USER': os.getenv('LM_DB_USER'),
        'PASSWORD': os.getenv('LM_DB_PASS'),
        'HOST': os.getenv('LM_DB_HOST'),
        'PORT': '',
        'TEST': {
            'NAME': '',
        },
        'CONN_MAX_AGE': 600,
    },
}

# FIXME: Change to read from env variable
if 'test' in sys.argv:
    DATABASES = {
        'default': {
            # 'ENGINE': 'django.db.backends.sqlite3',
            # 'NAME': os.getenv('LM_DB_NAME'),
            # 'PORT': '',
        },
    }

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': '{host}:{port}'.format(
            host=REDIS_HOST,
            port=REDIS_PORT
        ),
    },
}

if CACHE:
    CACHE_MIDDLEWARE_ALIAS = 'default'
    CACHE_MIDDLEWARE_SECONDS = CACHE_SECONDS
    CACHE_MIDDLEWARE_KEY_PREFIX = ''
    CACHES['default']['TIMEOUT'] = CACHE_SECONDS
    CACHES['default']['OPTIONS'] = {
        'MAX_ENTRIES': 500
    }

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

USE_I18N = True
LANGUAGE_CODE = 'en'
TIME_ZONE = 'UTC'
# TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
# NOSE_ARGS = [
    # '--with-coverage',
    # '--cover-package=api, vocabulary, ctasks',
# ]

ROSETTA_MESSAGES_PER_PAGE = 100
ROSETTA_STORAGE_CLASS = 'rosetta.storage.CacheRosettaStorage'

# USE_L10N = True
# USE_TZ = True

EMAIL_USE_TLS = bool(int(os.getenv('LM_EMAIL_USE_TLS', 1)))
EMAIL_USE_SSL = bool(int(os.getenv('LM_EMAIL_USE_SSL', 0)))
EMAIL_HOST = os.getenv('LM_EMAIL_HOST')
EMAIL_PORT = int(os.getenv('LM_EMAIL_PORT', 1234))
EMAIL_HOST_USER = os.getenv('LM_EMAIL_HOST_USER')
EMAIL_FROM = os.getenv('LM_EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('LM_EMAIL_HOST_PASSWORD')
EMAIL_BACKEND = os.getenv('LM_EMAIL_BACKEND')

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, "static"),
)

MEDIA_URL = '/media/'
MEDIA_ROOT = os.getenv('LM_MEDIA_ROOT')

LOCALE_PATHS = (
    os.path.join(PROJECT_ROOT, 'locale'),
)

# In MEDIA_ROOT
AVATARS_URL = 'avatar/'
AVATARS_URL_FULL = '{0}{1}'.format(
    MEDIA_ROOT,
    AVATARS_URL
)

LOGIN_URL = '/'

# True if registration needs to be confirmed by email
REGISTRATION_CONFIRMATION = False
LOGIN_AFTER_REGISTRATION = True
SEND_EMAIL_AFTER_REGISTRATION = True
SUPERADMIN_EMAIL = os.getenv('LM_SUPERADMIN_EMAIL', '').split(',')

CELERY_ACCEPT_CONTENT = ['json']
CELERY_HOST = REDIS_HOST
CELERY_PORT = REDIS_PORT
BROKER_URL = 'redis://{host}:{port}/'.format(
    host=CELERY_HOST,
    port=CELERY_PORT
)
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_IMPORTS = (
    "ctasks.game_tasks",
    "ctasks.dataset_tasks",
    "ctasks.admin_tasks"
)
CELERY_TIMEZONE = 'UTC'

from celery.schedules import crontab
from datetime import timedelta

CELERYBEAT_SCHEDULE = {
    'update_users_stats_all': {
        'task': 'ctasks.game_tasks.update_all_users_stats',
        'schedule': crontab(hour=4, minute=0),
    },
    'synchronise': {
        'task': 'ctasks.dataset_tasks.sync_word_counts',
        'schedule': crontab(hour=2, minute=0),
    },


    # Email

    'send_queued_mail': {
        'task': 'ctasks.admin_tasks.send_queued_mail',
        # 'schedule': crontab(seconds=30),
        'schedule' : timedelta(seconds=100)
    },

    'send_test_email': {
        'task': 'ctasks.admin_tasks.send_test_email',
        'schedule': crontab(hour='*/1', minute=0),
        # 'schedule' : timedelta(seconds=30)
    },
}
