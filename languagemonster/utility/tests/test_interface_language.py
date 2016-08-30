from mock import MagicMock

from utility.user_language import (
    landing_language,
    _get_default_language,
)

from utility import user_language

from utility.tests import const_language as cl

mock_request = MagicMock()

user_language.BASE_LANGUAGES = dict(
    en_uk=cl.BASE_GB,
    en_us=cl.BASE_US,
    en_au=cl.BASE_AU,
    de_de=cl.BASE_DE,
    de_at=cl.BASE_AT,
    pl_pl=cl.BASE_PL,
)

test_set = [
    (
        cl.BASE_US,
        'en,en-US;q=0.8,pl;q=0.6,en-ZA;q=0.4,en-AU;q=0.2,de-AT;'
        'q=0.2,de;q=0.2',
    ),
    (
        cl.BASE_US,
        'en-US;q=0.8,pl;q=0.6,en-ZA;q=0.4,en-AU;q=0.2,de-AT;q=0.2,de;q=0.2',
    ),
    (
        cl.BASE_DE,
        'fr,en-ZA;q=0.4,en-AU;q=0.2,de-AT;'
    ),
    (
        cl.BASE_DE,
        'fr',
    ),
    (
        cl.BASE_DE,
        'fr;q=0.8,pl;q=0.6,en-ZA;q=0.4,en-AU;q=0.2,de-AT;q=0.2,de;q=0.2',
    ),
    (
        cl.BASE_GB, '',
    ),
    (
        cl.BASE_DE, None
    ),
    (
        cl.BASE_AT,
        'de-AT;q=0.8,de-DE;q=0.6,en-ZA;q=0.4,en-AU;q=0.2,de-AT;q=0.2,de;q=0.2',
    ),
    (
        cl.BASE_DE,
        'de;q=0.8,de-DE;q=0.6,en-ZA;q=0.4,en-AU;q=0.2,de-AT;q=0.2,de;q=0.2',
    ),
    (
        cl.BASE_PL,
        'pl-pl;q=0.8,pl;q=0.6,en-ZA;q=0.4,en-AU;q=0.2,de-AT;q=0.2,de;q=0.2',
    ),
    (
        cl.BASE_PL,
        'pl;q=0.8,en;q=0.6,en-ZA;q=0.4,en-AU;q=0.2,de-AT;q=0.2,de;q=0.2',
    ),
    (
        cl.BASE_AT,
        'de-zh;q=0.8,en;q=0.6,en-ZA;q=0.4,en-AU;q=0.2,de-AT;q=0.2,de;q=0.2',
    ),
    (
        cl.BASE_DE,
        'es-ES',
    )
]

def test_interface_language_internals():

    for test in test_set:
        if test[1] is None:
            mock_request.META = {}
        else:
            mock_request.META = dict(HTTP_ACCEPT_LANGUAGE=test[1])

        base = _get_default_language(mock_request)

        assert base.symbol == test[0].symbol

def test_interface_language_from_cookies():
    mock_request.COOKIES = dict(monster_language='pl_pl')

    lang = landing_language(mock_request)

    assert lang.symbol == 'pl_pl'
