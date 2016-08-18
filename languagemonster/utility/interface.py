import hashlib
import time
import math
import uuid
import logging
from functools import wraps

from django.contrib import messages
from django.utils import translation
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from core.models import (
    MonsterUser,
    BaseLanguage,
    Progression,
)

from utility.user_language import landing_language
from utility.context import Context
from utility.url import get_urls

from core.data.base_language import BASE_LANGUAGES
from core.data.language_pair import LANGUAGE_PAIRS_FLAT
from core.data.language import LANGUAGES

logger = logging.getLogger(__name__)
settings.LOGGER(logger, settings.LOG_WWW_HANDLER)

def get_context(request):
    context = {}
    # context['basic'] = _get_status(request)
    # context['user'] = context['basic']['user']

    # context['context'] = Context(request)

    return Context(request)


def context(func):
    @wraps(func)
    def _func(*args):
        # args[0] is expect to be a Request object
        try:
            return func(*args, ctx=get_context(args[0]))
        except TypeError as e:
            logger.warning(str(e))
            return func(*args)

    return _func


def redirect_unauth(func):
    @wraps(func)
    def _func(*args, **kwargs):
        if kwargs.get('ctx', {}).get('user') is None:
            logger.info(
                'Unauthorized request. args: %s kwargs: %s',
                str(args),
                str(kwargs)
            )
            return HttpResponseRedirect(reverse('index'))
        return func(*args, **kwargs)
    return _func


def create_hash(muser):

    if muser:
        return hashlib.sha224(
            str(time.time()) + str(muser.user.email)
        ).hexdigest()
    else:
        return hashlib.sha1(str(time.time())).hexdigest()

def get_uuid_str():
    return uuid.uuid4().hex

def obfuscate(str, char='*', half=1):
    '''
        mjlechowski -> mjlech*****
    '''

    length = len(str)

    if length < 5:
        return '****'

    new_str = list(str)

    if half == 1:
        start, end = 0, math.ceil(length / 2)
    else:
        start, end = math.ceil(length / 2), length

    for i, c in enumerate(new_str):
        if i >= start and i < end:
            new_str[i] = '*'

    return ''.join(new_str)

def get_lang(slug):
    for lang in LANGUAGES.itervalues():
        if lang.slug == slug:
            return lang

    return None

def get_lang_pair_from_langs(base_lang, target_lang):
    for lang_pair in LANGUAGE_PAIRS_FLAT.itervalues():
        if (
            lang_pair.base_language == base_lang and
            lang_pair.target_language == target_lang
        ):
            return lang_pair

    return None

def get_lang_pair_from_slugs(base_slug, target_slug):
    for lang_pair in LANGUAGE_PAIRS_FLAT.itervalues():
        if (
            lang_pair.base_language.slug == base_slug and
            lang_pair.target_language.slug == target_slug
        ):
            return lang_pair

    return None

def get_base_lang(symbol):
    return BASE_LANGUAGES[symbol]

def get_progression_from_lang_pair(
    progressions,
    lang_pair
):
    for pair, progression in progressions:
        if pair == lang_pair:
            return progression

    return None

def _get_status(request):
    status_resp = {}

    status_resp['status'] = dict(
        debug=settings.DEBUG,
        version=settings.VERSION,
        branch=settings.BRANCH,
    )
    status_resp['base_languages'] = BASE_LANGUAGES
    status_resp['urls'] = get_urls(request)
    status_resp['messages'] = messages.get_messages(request)

    authorised = False

    pk = request.session.get('_auth_user_id')

    if pk is None:
        authorised = False
    else:
        monster_user = MonsterUser.objects.filter(
            user__id=pk
        ).select_related('user').first()

        if monster_user is None:
            authorised = False
        else:
            authorised = monster_user.user.is_authenticated()

    if authorised:
        add_context_authorised(status_resp, monster_user)
    else:
        add_context_unauthorised(status_resp, request)

    return status_resp

def add_context_unauthorised(status_resp, request):
    status_resp['user'] = None
    status_resp['user_lang'] = None
    base = landing_language(request)

    try:
        translation.activate(base.language.acronym)
    except Exception as e:
        logger.critical(
            "Cannot change user language: %s",
            e
        )
        translation.activate('en')

def add_context_authorised(status_resp, monster_user):
    status_resp['user'] = monster_user
    status_resp['user_lang'] = BASE_LANGUAGES.get(monster_user.language)

    status_resp['studying'] = [
        (
            p,
            LANGUAGE_PAIRS_FLAT.get(
                p.lang_pair
            )
        )
        for p in Progression.objects.filter(
            user=monster_user
        )
    ]

    status_resp['studying'] = filter(
        lambda x: x[1].base_language.acronym == status_resp['user_lang'].language.acronym,
        status_resp['studying']
    )

    try:
        acronym = BASE_LANGUAGES[monster_user.language].language.acronym
        translation.activate(acronym)
    except Exception as e:
        logger.critical(
            "Cannot change user language: %s",
            e
        )
        translation.activate('en')
