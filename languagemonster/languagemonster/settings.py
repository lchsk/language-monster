from __future__ import absolute_import

import logging.config
import sys
import os
from datetime import timedelta

from django.utils.translation import ugettext_lazy as _

from celery.schedules import crontab

ID = 'languagemonster'
VERSION = '0.1.0'
BRANCH = 'master'

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = os.getenv('LM_SECRET_KEY', '123456789')
API_KEY = os.getenv('LM_API_KEY')

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

LOG_FORMAT = ('%(asctime)s %(levelname)s %(name)s '
                '%(funcName)s:%(lineno)d %(message)s')

LOG_DIR = os.getenv('LM_LOG_DIR', './')

LOGGING_CONFIG = None

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': LOG_FORMAT,
        },
    },
    'handlers': {
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'log_file':{
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join('./', 'monster.log'),
            'maxBytes': 20 * 1024 * 1024,
            'backupCount': 20,
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['log_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'apps': {
            'handlers': ['log_file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django': {
            'handlers': ['log_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
    'root': {
        'handlers': ['log_file', 'console'],
        'level': 'DEBUG'
    },
}

logging.config.dictConfig(LOGGING)

ALLOWED_HOSTS = os.getenv('LM_ALLOWED_HOSTS', '').split(',')

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

GAMES_USE_CANVAS_ONLY = False

# Number of word pairs user learns during a game level
GAMES_DEFAULT_WORDS_COUNT = 4 if DEBUG else 8

# Number of word sets returned in a single (default) call
GAMES_DEFAULT_WORD_SETS_COUNT = 10

GAMES = {
    'space': {
        'available': True,
        'name': _('game_space_game'),
        'image': 'space.png',
        'prod': True,
    },
    'simple': {
        'available': True,
        'name': _('game_four_buttons'),
        'image': 'simple.png',
        'prod': False,
    },
    'plane': {
        'available': True,
        'name': _('game_crazy_plane'),
        'image': 'plane.png',
        'prod': True,
    },
    'runner': {
        'available': True,
        'name': _('game_bunny_runner'),
        'image': 'runner.png',
        'prod': True,
    },
    'shooter': {
        'available': True,
        'name': _('game_word_sniper'),
        'image': 'shooter.png',
        'prod': True,
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

    # 3rd party
    'debug_toolbar',
    'sysmon',
    'sorl.thumbnail',
    'rosetta',
    'post_office',
    'rest_framework',
    'django_countries',

    # Apps
    'core',
    'api',
    'vocabulary',
    'ctasks',
    'userprofile',
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
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '20/minute',
    },
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

ROSETTA_MESSAGES_PER_PAGE = 100
ROSETTA_STORAGE_CLASS = 'rosetta.storage.CacheRosettaStorage'

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
MEDIA_ROOT = './tmp/media/' if DEBUG else os.getenv('LM_MEDIA_ROOT')

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
    'ctasks.game_tasks',
    'ctasks.dataset_tasks',
    'ctasks.admin_tasks',
)
CELERY_TIMEZONE = 'UTC'

CELERYBEAT_SCHEDULE = {
    'update_users_stats_all': {
        'task': 'ctasks.game_tasks.update_all_users_stats',
        'schedule': crontab(hour=4, minute=0),
    },
    'synchronise': {
        'task': 'ctasks.dataset_tasks.sync_word_counts',
        'schedule': crontab(hour=2, minute=0),
    },
    'send_queued_mail': {
        'task': 'ctasks.admin_tasks.send_queued_mail',
        'schedule': timedelta(seconds=60)
    },
    'send_test_email': {
        'task': 'ctasks.admin_tasks.send_test_email',
        'schedule': crontab(hour='*/1', minute=0),
    },
}
