# -*- coding: utf-8 -*-

from collections import namedtuple
from core.data.language import LANGUAGES

BaseLanguage = namedtuple('BaseLanguage', [
    'flag_filename',
    'original_name',
    'country',
    'language',
    'symbol',
])

# Format: language_country

pt_pt = BaseLanguage(
    flag_filename="pt",
    original_name=u"Português",
    country=u"pt",
    language=LANGUAGES['pt'],
    symbol=u'pt_pt',
)

it_it = BaseLanguage(
    flag_filename=u"it",
    original_name=u"Italiano",
    country=u"it",
    language=LANGUAGES['it'],
    symbol=u'it_it',
)

fr_fr = BaseLanguage(
    flag_filename=u"fr",
    original_name=u"Français",
    country=u"fr",
    language=LANGUAGES['fr'],
    symbol=u'fr_fr',
)

es_es = BaseLanguage(
    flag_filename=u"es",
    original_name=u"Español",
    country=u"es",
    language=LANGUAGES['es'],
    symbol=u'es_es',
)

en_ca = BaseLanguage(
    flag_filename=u"ca",
    original_name=u"English (CA)",
    country=u"ca",
    language=LANGUAGES['en'],
    symbol=u'en_ca',
)

en_au = BaseLanguage(
    flag_filename=u"au",
    original_name=u"English (AU)",
    country=u"au",
    language=LANGUAGES['en'],
    symbol=u'en_au',
)

en_uk = BaseLanguage(
    flag_filename=u"uk",
    original_name=u"English (UK)",
    country=u"gb",
    language=LANGUAGES['en'],
    symbol=u'en_uk',
)

en_us = BaseLanguage(
    flag_filename=u"us",
    original_name=u"English (US)",
    country=u"us",
    language=LANGUAGES['en'],
    symbol=u'en_us',
)

en_nz = BaseLanguage(
    flag_filename=u"nz",
    original_name=u"English (NZ)",
    country=u"nz",
    language=LANGUAGES['en'],
    symbol=u'en_nz',
)

pl_pl = BaseLanguage(
    flag_filename=u"pl",
    original_name=u"Polski",
    country=u"pl",
    language=LANGUAGES['pl'],
    symbol=u'pl_pl',
)

de_de = BaseLanguage(
    flag_filename=u"de",
    original_name=u"Deutsch",
    country=u"de",
    language=LANGUAGES['de'],
    symbol=u'de_de',
)

BASE_LANGUAGES = dict(
    pl_pl=pl_pl,
    # de_de=de_de,
    # es_es=es_es,
    # fr_fr=fr_fr,
    # pt_pt=pt_pt,
    # it_it=it_it,
    en_uk=en_uk,
    en_us=en_us,
    en_nz=en_nz,
    en_au=en_au,
    en_ca=en_ca,
)

# 46;"hu";"magyar";"hu";f;41
# 45;"hr";"hrvatski jezik";"hr";f;57
# 44;"gr";"ελληνικά";"gr";f;51
# 43;"ge";"ქართული";"ge";f;59
# 41;"fi";"suomi";"fi";f;39
# 39;"ee";"eesti";"ee";f;47
# 38;"dk";"dansk";"dk";f;65
# 37;"cz";"čeština";"cz";f;43
# 36;"by";"беларуская мова";"by";f;62
# 35;"bg";"български език";"bg";f;54
# 34;"am";"Հայերեն";"hy";f;56
# 33;"al";"Shqip";"al";f;55
# 32;"ru";"Русский";"ru";f;63
# 31;"ca";"English (CA)";"ca";t;66
# 30;"nz";"English (NZ)";"nz";t;66
# 29;"au";"English (AU)";"au";t;66
# 28;"de";"Deutsch";"de";f;36
# 27;"pl";"Polski";"pl";t;70
# 26;"uk";"English (UK)";"gb";t;66
# 25;"us";"English (US)";"us";t;66
