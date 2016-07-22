# -*- coding: utf-8 -*-

from collections import namedtuple
from core.language import LANGUAGES

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
    country="pt",
    language=LANGUAGES['pt'],
    symbol='pt_pt',
)

it_it = BaseLanguage(
    flag_filename="it",
    original_name=u"Italiano",
    country="it",
    language=LANGUAGES['it'],
    symbol='it_it',
)

fr_fr = BaseLanguage(
    flag_filename="fr",
    original_name=u"Français",
    country="fr",
    language=LANGUAGES['fr'],
    symbol='fr_fr',
)

es_es = BaseLanguage(
    flag_filename="es",
    original_name=u"Español",
    country="es",
    language=LANGUAGES['es'],
    symbol='es_es',
)

en_ca = BaseLanguage(
    flag_filename="ca",
    original_name=u"English (CA)",
    country="ca",
    language=LANGUAGES['en'],
    symbol='en_ca',
)

en_au = BaseLanguage(
    flag_filename="au",
    original_name=u"English (AU)",
    country="au",
    language=LANGUAGES['en'],
    symbol='en_au',
)

en_uk = BaseLanguage(
    flag_filename="uk",
    original_name=u"English (UK)",
    country="gb",
    language=LANGUAGES['en'],
    symbol='en_uk',
)

en_us = BaseLanguage(
    flag_filename="us",
    original_name=u"English (US)",
    country="us",
    language=LANGUAGES['en'],
    symbol='en_us',
)

en_nz = BaseLanguage(
    flag_filename="nz",
    original_name=u"English (NZ)",
    country="nz",
    language=LANGUAGES['en'],
    symbol='en_nz',
)

pl_pl = BaseLanguage(
    flag_filename="pl",
    original_name=u"Polski",
    country="pl",
    language=LANGUAGES['pl'],
    symbol='pl_pl',
)

de_de = BaseLanguage(
    flag_filename="de",
    original_name=u"Deutsch",
    country="de",
    language=LANGUAGES['de'],
    symbol='de_de',
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
