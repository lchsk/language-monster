import hashlib
import time
import math
import uuid
import logging
from collections import OrderedDict
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

from utility.url import get_urls
from core.data.base_language import BASE_LANGUAGES
from core.data.language_pair import LANGUAGE_PAIRS_FLAT
from core.data.language import LANGUAGES

logger = logging.getLogger(__name__)
settings.LOGGER(logger, settings.LOG_WWW_HANDLER)

def get_user(request):
    """Returns Monster User"""

    return MonsterUser.objects.filter(user=request.user).first()


def get_basics(request):
    d = {}

    d['status'] = dict(
        debug=settings.DEBUG,
        version=settings.VERSION,
    )
    d['base_languages'] = BASE_LANGUAGES
    d['urls'] = get_urls(request)
    d['messages'] = messages.get_messages(request)

    authorized = False

    pk = request.session.get('_auth_user_id')

    if pk is None:
        authorized = False
    else:
        muser = MonsterUser.objects.filter(
            user__id=pk
        ).select_related(
            'user',
        ).first()

        if muser is None:
            authorized = False
        else:
            authorized = muser.user.is_authenticated()

    if authorized:
        d['user'] = muser
        d['user_lang'] = BASE_LANGUAGES.get(muser.language)
        # TODO:

        # progressions = Progression.objects.filter(
        #     user=muser,
        #     # lang_pair=muser.lang.language.acronym
        #     # pair__base_language=muser.current_language
        # )

        d['studying'] = [
            (
                p,
                LANGUAGE_PAIRS_FLAT.get(
                    p.lang_pair
                )
            )
            for p in Progression.objects.filter(
                user=muser
            )
        ]

        d['studying'] = filter(
            lambda x: x[1].base_language.acronym == d['user_lang'].language.acronym,
            d['studying']
        )

        try:
            acronym = BASE_LANGUAGES[muser.language].language.acronym
            translation.activate(acronym)
        except Exception as e:
            logger.critical(
                "Cannot change user language: %s",
                e
            )
            translation.activate('en')
    else:
        d['user'] = None
        d['user_lang'] = None
        base = landing_language(request)

        try:
            translation.activate(
                base.language.acronym
            )
        except Exception as e:
            logger.critical(
                "Cannot change user language: %s",
                e
            )            
            translation.activate('en')

    return d


def _get_def_lang(request):
    '''Finds user's default language, based on the browser's settings'''

    defaults = OrderedDict()
    defaults['en'] = 'gb'
    defaults['de'] = 'de'

    bases = BASE_LANGUAGES
    preferred_lang = OrderedDict()

    if 'HTTP_ACCEPT_LANGUAGE' in request.META:
        langs = request.META.get('HTTP_ACCEPT_LANGUAGE', ['en', ])
        langs = langs.replace(';', ',').replace('_', '-').lower()

        if ',' not in langs:
            langs = langs + ','

        country = ''

        for lang in langs.split(','):
            if lang and '=' not in lang:
                if '-' in lang:
                    code, country = lang.split('-')

                    if code and code not in preferred_lang:
                        preferred_lang[code] = []

                    preferred_lang[code].append(country)
                else:
                    if lang not in preferred_lang:
                        preferred_lang[lang] = []

        for def_lang, def_country in defaults.iteritems():
            if def_lang not in preferred_lang:
                preferred_lang[def_lang] = []
            preferred_lang[def_lang].append(def_country)

        # Take the first one
        lang, countries = next(preferred_lang.iteritems())

        if not lang:
            lang = 'en'

        default = None

        if not countries:
            countries.append(lang)

        for country in countries:
            for base in bases.itervalues():
                acronym = base.language.acronym

                if (
                    acronym == lang and
                    base.country == country
                ):
                    return base

                if (
                    lang == acronym and
                    defaults.get(acronym) == base.country
                ):
                    default = base

        if default is not None:
            return default

            # if len(lang) == 2:
            #     if lang in defaults.keys():
            #         country = defaults[lang]
            # 
            #     if country:
            #         for b in bases:
            #             if b.language.acronym == lang and b.country == country:
            #                 return b
            #     else:
            #         for b in bases:
            #             if b.language.acronym == lang:
            #                 return b
            # elif len(lang) == 5:
            #     separator = ''
            # 
            #     if '-' in lang:
            #         separator = '-'
            #     elif '_' in lang:
            #         separator = '_'
            #     else:
            #         break
            # 
            #     lcode, ccode = lang.split(separator)
            # 
            #     for b in bases:
            #         if b.country == ccode and b.language.acronym == lcode:
            #             return b



    for b in bases.itervalues():
        acronym = b.language.acronym

        if (
            acronym in defaults.keys() and
            b.country == defaults[acronym]
        ):
            return b

    return False


def landing_language(request):

    if (
        'monster_language' in request.COOKIES and
        request.COOKIES['monster_language'] in BASE_LANGUAGES
    ):
        return BASE_LANGUAGES[
            request.COOKIES['monster_language']
        ]
    else:
        return _get_def_lang(request)


def find_base_language(locale):
    '''locale eg. en_GB. (For social account) TODO: needs SQL optimization'''

    locale = locale.lower()

    separator = ''

    if '_' in locale:
        separator = '_'
    elif '-' in locale:
        separator = '-'
    elif len(locale) == 2:
        return BaseLanguage.objects(country='gb').first()

    if separator:
        lang, country = locale.split(separator)

        b = BaseLanguage.objects(country=country).first()

        if b:
            return b
        else:
            return BaseLanguage.objects(country='gb').first()
    else:
        return False


def get_context(request):

    d = {}
    d['basic'] = get_basics(request)
    d['user'] = d['basic']['user']

    return d


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
    return uuid.uuid4().hex.replace('-', '')


def obfuscate(str, char='*', half=1):
    '''
        mjlechowski -> mjlech*****
    '''

    length = len(str)

    if length < 5:
        return '****'

    new_str = list(str)

    # print new_str == str, new_str is str

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
