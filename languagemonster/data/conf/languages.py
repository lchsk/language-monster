# -*- encoding: utf-8 -*-

# In this file: only configuration that does not depend on other files

# List of languages that should be well defined

WORKING_LANGUAGES = (
    'pl', 'en', 'it', 'pt', 'de', 'es', 'fr',
)

t = {}

t['en'] = dict(
    name='English',
    own_name=u'English',
    english='English',
    acronym='en',
    raw_table='en',
    raw=None,
    data=None,
    clinks=None,
    pos={
        'Noun': u'Noun',
        'Proper noun': u'Proper noun',
        'Verb': u'Verb',
        'Adverb': u'Adverb',
        'Adjective': u'Adjective',
    },
    languages=dict(
        pl='Polish',
        en='English',
        it='Italian',
        pt='Portuguese',
        de='German',
        es='Spanish',
        fr='French',
    )
)

t['pl'] = dict(
    name='Polish',
    own_name=u'język polski',
    english='język angielski',
    acronym='pl',
    raw_table='pl',
    raw=None,
    data=None,
    clinks=None,
    pos={
        'Noun': 'rzeczownik',
        'Proper noun': 'nazwa własna',
        'Verb': u'czasownik',
        'Adverb': u'przysłówek',
        'Adjective': u'przymiotnik',
    },
    languages=dict(
        pl='język polski',
        en='język angielski',
        it='język włoski',
        pt='język portugalski',
        de='język niemiecki',
        es='język hiszpański',
        fr='język francuski',
    )
)

t['pt'] = dict(
    name='Portuguese',
    own_name=u'-pt-',
    english='inglês',
    acronym='pt',
    raw_table='pt',
    raw=None,
    data=None,
    clinks=None,
    pos={
        'Noun': u'Substantivo',
        'Proper noun': 'Substantivo',
        'Verb': u'Verbo',
        'Adverb': u'Advérbio',
        'Adjective': u'Adjetivo',
    },
    languages=dict(
        pl='-pl-',
        en='-en-',
        it='-it-',
        pt='-pt-',
        de='-de-',
        es='-es-',
        fr='-fr-',
    )
)

t['it'] = dict(
    name='Italian',
    own_name=u'-it-',
    english='',
    acronym='it',
    raw_table='it',
    raw=None,
    data=None,
    clinks=None,
    pos={
        'Noun': u'sost',
        'Proper noun': 'nome',
        'Verb': u'verb',
        'Adverb': u'adv',
        'Adjective': u'agg',
    },
    languages=dict(
        pl='-pl-',
        en='-en-',
        it='-it-',
        pt='-pt-',
        de='-de-',
        es='-es-',
        fr='-fr-',
    )
)

t['de'] = dict(
    name='German',
    own_name=u'Deutsch',
    english='',
    acronym='de',
    raw_table='de',
    raw=None,
    data=None,
    clinks=None,
    pos={
        'Noun': u'Substantiv',
        'Proper noun': 'Bedeutungen',
        'Verb': u'Verb',
        'Adverb': u'Adverb',
        'Adjective': u'Adjektiv',
    },
    languages=dict(
        pl='Polnisch',
        en='Englisch',
        it='Italienisch',
        pt='Portugiesisch',
        de='Deutsch',
        es='Spanisch',
        fr='Französisch',
    )
)

t['es'] = dict(
    name='Spanish',
    own_name=u'es',
    english='',
    acronym='es',
    raw_table='es',
    raw=None,
    data=None,
    clinks=None,
    pos={
        'Noun': 'sustantivo',
        'Proper noun': 'sustantivo propio',
        'Verb': u'verbo',
        'Adverb': u'adverbio',
        'Adjective': u'adjetivo',
    },
    languages=dict(
        pl='pl',
        en='en',
        it='it',
        pt='pt',
        de='de',
        es='es',
        fr='fr',
    )
)

t['fr'] = dict(
    name='French',
    own_name=u'fr',
    english='',
    acronym='fr',
    raw_table='fr',
    raw=None,
    data=None,
    clinks=None,
    pos={
        'Noun': u'nom',
        'Proper noun': 'nom propre',
        'Verb': u'verbe',
        'Adverb': u'adverbe',
        'Adjective': u'adjectif',
    },
    languages=dict(
        pl='pl',
        en='en',
        it='it',
        pt='pt',
        de='de',
        es='es',
        fr='fr',
    )
)

MANDATORY_FIELDS = (
    'name',
    'own_name',
    'english',
    'acronym',
    'raw_table',
    'raw',
    'data',
    'clinks',
    'pos',
    'languages',
)

DICTIONARIES = ('pos', 'languages')

def validate(language):
    """
        checks if language definitions are valid
    """

    if language not in t:
        raise Exception("{lang} is not defined".format(lang=language))

    _t = t[language]

    if not isinstance(t, dict):
        raise Exception("Definitions should look like a dictionary")

    for i in MANDATORY_FIELDS:
        if i not in _t:
            raise Exception("{field} is a mandatory field".format(field=i))

    for i in DICTIONARIES:
        if not isinstance(_t[i], dict):
            raise Exception("{field} should be a dictionary".format(field=i))

    _languages = _t['languages']

    for i in WORKING_LANGUAGES:
        if i not in _languages:
            raise Exception("{failed_acronym} is not defined in {acronym}.\n\
Following languages must be defined: {all}".format(
                failed_acronym = i,
                acronym = language,
                all = ', '.join(WORKING_LANGUAGES)
            ))
