# -*- coding: utf-8 -*-

from collections import namedtuple
from core.data.language import LANGUAGES

class LanguagePair(namedtuple('LanguagePair', [
    'base_language',
    'target_language',
    'visible',
    'symbol',
])):
    __slots__ = ()

    def __unicode__(self):
        return u'{} -> {}'.format(self.base_language, self.target_language)

# Same language as base and target

en_en = LanguagePair(
    base_language=LANGUAGES['en'],
    target_language=LANGUAGES['en'],
    visible=False,
    symbol=u'en_en',
)

pl_pl = LanguagePair(
    base_language=LANGUAGES['pl'],
    target_language=LANGUAGES['pl'],
    visible=False,
    symbol=u'pl_pl',
)

# Base: Polish

pl_en = LanguagePair(
    base_language=LANGUAGES['pl'],
    target_language=LANGUAGES['en'],
    visible=True,
    symbol=u'pl_en',
)

pl_es = LanguagePair(
    base_language=LANGUAGES['pl'],
    target_language=LANGUAGES['es'],
    visible=True,
    symbol=u'pl_es',
)

pl_fr = LanguagePair(
    base_language=LANGUAGES['pl'],
    target_language=LANGUAGES['fr'],
    visible=True,
    symbol=u'pl_fr',
)

pl_de = LanguagePair(
    base_language=LANGUAGES['pl'],
    target_language=LANGUAGES['de'],
    visible=True,
    symbol=u'pl_de',
)

pl_it = LanguagePair(
    base_language=LANGUAGES['pl'],
    target_language=LANGUAGES['it'],
    visible=True,
    symbol=u'pl_it',
)

pl_pt = LanguagePair(
    base_language=LANGUAGES['pl'],
    target_language=LANGUAGES['pt'],
    visible=True,
    symbol=u'pl_pt',
)

# Base: English

en_pl = LanguagePair(
    base_language=LANGUAGES['en'],
    target_language=LANGUAGES['pl'],
    visible=True,
    symbol=u'en_pl',
)

en_es = LanguagePair(
    base_language=LANGUAGES['en'],
    target_language=LANGUAGES['es'],
    visible=True,
    symbol=u'en_es',
)

en_fr = LanguagePair(
    base_language=LANGUAGES['en'],
    target_language=LANGUAGES['fr'],
    visible=True,
    symbol=u'en_fr',
)

en_de = LanguagePair(
    base_language=LANGUAGES['en'],
    target_language=LANGUAGES['de'],
    visible=True,
    symbol=u'en_de',
)

en_it = LanguagePair(
    base_language=LANGUAGES['en'],
    target_language=LANGUAGES['it'],
    visible=True,
    symbol=u'en_it',
)

en_pt = LanguagePair(
    base_language=LANGUAGES['en'],
    target_language=LANGUAGES['pt'],
    visible=True,
    symbol=u'en_pt',
)

LANGUAGE_PAIRS_ALL = dict(
    en=dict(
        en_en=en_en,
        en_pl=en_pl,
        en_it=en_it,
        en_de=en_de,
        en_fr=en_fr,
        en_pt=en_pt,
        en_es=en_es,
    ),
    pl=dict(
        pl_pl=pl_pl,
        pl_en=pl_en,
        pl_it=pl_it,
        pl_de=pl_de,
        pl_fr=pl_fr,
        pl_pt=pl_pt,
        pl_es=pl_es,
    )
)

LANGUAGE_PAIRS = {}

for k, v in LANGUAGE_PAIRS_ALL.items():
    for symbol, pair in v.items():
        if k not in LANGUAGE_PAIRS:
            LANGUAGE_PAIRS[k] = {}

        if pair.visible:
            LANGUAGE_PAIRS[k][symbol] = pair

LANGUAGE_PAIRS_FLAT_ALL = {}

for lang_dict in LANGUAGE_PAIRS_ALL.values():
    for symbol, data in lang_dict.iteritems():
        LANGUAGE_PAIRS_FLAT_ALL[symbol] = data


LANGUAGE_PAIRS_FLAT = {}

for lang_dict in LANGUAGE_PAIRS.values():
    for symbol, data in lang_dict.iteritems():
        LANGUAGE_PAIRS_FLAT[symbol] = data

def get_language_pair(base, target):
    for _, lang_pair in LANGUAGE_PAIRS[base].iteritems():
        if lang_pair.target_language.acronym == target:
            return lang_pair

    return None
