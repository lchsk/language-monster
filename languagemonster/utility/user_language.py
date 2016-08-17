from collections import OrderedDict

from core.data.base_language import BASE_LANGUAGES

def landing_language(request):
    language = BASE_LANGUAGES.get(request.COOKIES.get('monster_language'))

    if language is None:
        return _get_default_language(request)
    else:
        return language

def _get_default_language(request):
    """Finds user's default language, based on the browser's settings"""

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

    for b in bases.itervalues():
        acronym = b.language.acronym

        if (
            acronym in defaults.keys() and
            b.country == defaults[acronym]
        ):
            return b

    return False
