import subprocess
import glob
import datetime
import os
from errno import errorcode

from celery.task.control import inspect
import redis
from redis import ConnectionError

from django.conf import settings

from core.models import (
    MonsterUser,
    DataSet,
)

from core.data.base_language import BASE_LANGUAGES
from core.data.language_pair import (
    LANGUAGE_PAIRS,
    LANGUAGE_PAIRS_FLAT,
)

def _get_celery_status():
    ERROR_KEY = "ERROR"

    try:
        insp = inspect()
        d = insp.stats()

        if not d:
            d = { ERROR_KEY: 'No running Celery workers were found.' }
    except IOError as e:
        msg = "Error connecting to the backend: {}".format(e)

        if len(e.args) > 0 and errorcode.get(e.args[0]) == 'ECONNREFUSED':
            msg += ' Check that the RabbitMQ server is running.'

        d = { ERROR_KEY: msg }
    except ImportError as e:
        d = { ERROR_KEY: str(e)}

    return d

def _count_users_logged_within(datetime_obj):
    return MonsterUser.objects.filter(user__last_login__gt=datetime_obj).count()

def _get_users_stats():
    t_5min = datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
    t_1h = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
    t_24h = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
    t_1w = datetime.datetime.utcnow() - datetime.timedelta(days=7)
    t_30d = datetime.datetime.utcnow() - datetime.timedelta(days=30)

    return dict(
        users_count=MonsterUser.objects.all().count(),
        superusers_count=MonsterUser.objects.filter(
            user__is_superuser=True
        ).count(),
        users_5min=_count_users_logged_within(t_5min),
        users_1h=_count_users_logged_within(t_1h),
        users_24h=_count_users_logged_within(t_24h),
        users_1w=_count_users_logged_within(t_1w),
        users_30d=_count_users_logged_within(t_30d),
    )

def _get_daemons_status():
    celerybeat = False
    redis_sorl = False
    redis_celery = False

    ps = subprocess.Popen(
        ['ps', 'aux'],
        stdout=subprocess.PIPE
    ).communicate()[0]

    processes = ps.split('\n')

    for p in processes:
        if 'celery' and settings.ID and 'beat' in p:
            celerybeat = True
            break

    redis_sorl = redis.Redis(
        host=settings.THUMBNAIL_REDIS_HOST,
        port=settings.THUMBNAIL_REDIS_PORT
    )
    redis_celery = redis.Redis(
        host=settings.CELERY_HOST,
        port=settings.CELERY_PORT
    )

    try:
        redis_sorl.ping()
        redis_sorl = True
    except ConnectionError:
        pass

    try:
        redis_celery.ping()
        redis_celery = True
    except ConnectionError:
        pass

    return dict(
        celerybeat=celerybeat,
        redis_sorl=redis_sorl,
        redis_celery=redis_celery,
    )

def _get_files_status():
    avatars_writable = os.access(settings.AVATARS_URL_FULL, os.W_OK)

    try:
        log_files = glob.glob('/tmp/*.log')

        logs = {}
        logs_count = len(log_files)

        for l in log_files:
            cmd = 'tail ' + l
            output = subprocess.check_output(['bash','-c', cmd])

            logs[l] = output
    except:
        pass

    return dict(
        avatars_writable=avatars_writable,
        logs=logs,
        logs_count=logs_count,
    )

def _get_settings():
    return dict(
        ID=settings.ID,
        BASE_DIR=settings.BASE_DIR,
        PROJECT_ROOT=settings.PROJECT_ROOT,
        DEBUG=settings.DEBUG,
        THUMBNAIL_FORMAT=settings.THUMBNAIL_FORMAT,
        ALLOWED_HOSTS=settings.ALLOWED_HOSTS,
        INSTALLED_APPS=sorted(settings.INSTALLED_APPS),
        USE_I18N=settings.USE_I18N,
        LANGUAGE_CODE=settings.LANGUAGE_CODE,
        TIME_ZONE=settings.TIME_ZONE,
        USE_L10N=settings.USE_L10N,
        USE_TZ=settings.USE_TZ,
        EMAIL_HOST_USER=settings.EMAIL_HOST_USER,
        STATICFILES_DIRS=settings.STATICFILES_DIRS,
        MEDIA_ROOT=settings.MEDIA_ROOT,
        AVATARS_ROOT=settings.AVATARS_URL_FULL,
        LOCALE_PATHS=settings.LOCALE_PATHS,
        REGISTRATION_CONFIRMATION=settings.REGISTRATION_CONFIRMATION,
        CELERYBEAT_SCHEDULE=settings.CELERYBEAT_SCHEDULE,
        CELERY='{}:{}'.format(settings.CELERY_HOST, settings.CELERY_PORT),
        REDIS='{}:{}'.format(
            settings.THUMBNAIL_REDIS_HOST,
            settings.THUMBNAIL_REDIS_PORT,
        )
    )

def _get_sets_status():
    sets = DataSet.objects.filter(visible=True)

    sets_per_lang_pair = {
        lang_pair: (
            sum(1 for s in sets if s.lang_pair == lang_pair),
            sum(s.word_count for s in sets if s.lang_pair == lang_pair),
        )
        for lang_pair in LANGUAGE_PAIRS_FLAT
    }

    acronyms = set(b.language.acronym for b in BASE_LANGUAGES.values())

    sets_per_lang = {
        acronym: (
            sum(
                sets_cnt
                for lang_pair, (sets_cnt, words_cnt) in sets_per_lang_pair.iteritems()
                if lang_pair[:2] == acronym
            ),
            sum(
                words_cnt
                for lang_pair, (sets_cnt, words_cnt) in sets_per_lang_pair.iteritems()
                if lang_pair[:2] == acronym
            )
        )
        for acronym in acronyms
    }

    return dict(
        sets_all_cnt=DataSet.objects.count(),
        sets_vis_cnt=len(sets),
        sets_per_lang=sets_per_lang,
        sets_per_lang_pair=sorted(sets_per_lang_pair.items()),
        words_cnt=sum(words_cnt for _, words_cnt in sets_per_lang.values()),
    )

def _get_languages_status():
    return dict(
        base_languages=BASE_LANGUAGES,
        language_pairs=LANGUAGE_PAIRS,
    )


def get_status_data():
    """Information needed to show the status view."""

    return dict(
        celery=_get_celery_status(),
        users=_get_users_stats(),
        daemons=_get_daemons_status(),
        settings=_get_settings(),
        files=_get_files_status(),
        languages=_get_languages_status(),
        sets=_get_sets_status(),
    )
