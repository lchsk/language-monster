import random
import uuid
import mock

import factory
from factory.fuzzy import (
    FuzzyAttribute,
    FuzzyText,
)

import unittest

from django.contrib.auth import models as contrib_models

from core.models import (
    Language,
    BaseLanguage,
    WordPair,
    UserWordPair,
    MonsterUser,
    MonsterUserGame,
)

from core.mock_models import (
    BaseLanguageFactory,
    LanguageFactory,
)

from utility.interface import (
    landing_language,
    _get_def_lang,
)

class RandomWebStuffTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_interface_language_internals(
        self
    ):
        mock_request = mock.MagicMock()

        lang_en = LanguageFactory(acronym='en')
        lang_de = LanguageFactory(acronym='de')
        lang_pl = LanguageFactory(acronym='pl')

        base_gb = BaseLanguageFactory(language=lang_en, country='gb')
        base_us = BaseLanguageFactory(language=lang_en, country='us')
        base_au = BaseLanguageFactory(language=lang_en, country='au')
        base_de = BaseLanguageFactory(language=lang_de, country='de')
        base_at = BaseLanguageFactory(language=lang_de, country='at')
        base_pl = BaseLanguageFactory(language=lang_pl, country='pl')

        base_languages = [base_gb, base_us, base_au, base_de, base_at, base_pl]

        # 1
        mock_request.META = {
            'HTTP_ACCEPT_LANGUAGE': 'en,en-US;q=0.8,pl;q=0.6,en-ZA;q=0.4,en-AU;q=0.2,de-AT;q=0.2,de;q=0.2'
        }
        base = _get_def_lang(mock_request, base_languages)
        self.assertEqual(base, base_us)

        # 2
        mock_request.META = {
            'HTTP_ACCEPT_LANGUAGE': 'en-US;q=0.8,pl;q=0.6,en-ZA;q=0.4,en-AU;q=0.2,de-AT;q=0.2,de;q=0.2'
        }

        base = _get_def_lang(mock_request, base_languages)
        self.assertEqual(base, base_us)

        # 3
        mock_request.META = {
            'HTTP_ACCEPT_LANGUAGE': 'fr,en-ZA;q=0.4,en-AU;q=0.2,de-AT;'
        }

        base = _get_def_lang(mock_request, base_languages)
        self.assertEqual(base, base_gb)

        # 4
        mock_request.META = {
            'HTTP_ACCEPT_LANGUAGE': 'fr'
        }

        base = _get_def_lang(mock_request, base_languages)
        self.assertEqual(base, base_gb)

        # 5 Only interested in the first one, otherwise -> English
        mock_request.META = {
            'HTTP_ACCEPT_LANGUAGE': 'fr;q=0.8,pl;q=0.6,en-ZA;q=0.4,en-AU;q=0.2,de-AT;q=0.2,de;q=0.2'
        }

        base = _get_def_lang(mock_request, base_languages)
        self.assertEqual(base, base_gb)

        # 6
        mock_request.META = {
            'HTTP_ACCEPT_LANGUAGE': ''
        }

        base = _get_def_lang(mock_request, base_languages)
        self.assertEqual(base, base_gb)

        # 7
        mock_request.META = {}

        base = _get_def_lang(mock_request, base_languages)
        self.assertEqual(base, base_gb)

        # 8
        mock_request.META = {
            'HTTP_ACCEPT_LANGUAGE': 'de-AT;q=0.8,de-DE;q=0.6,en-ZA;q=0.4,en-AU;q=0.2,de-AT;q=0.2,de;q=0.2'
        }

        base = _get_def_lang(mock_request, base_languages)
        self.assertEqual(base, base_at)

        # 9
        mock_request.META = {
            'HTTP_ACCEPT_LANGUAGE': 'de;q=0.8,de-DE;q=0.6,en-ZA;q=0.4,en-AU;q=0.2,de-AT;q=0.2,de;q=0.2'
        }

        base = _get_def_lang(mock_request, base_languages)
        self.assertEqual(base, base_de)

        # 10
        mock_request.META = {
            'HTTP_ACCEPT_LANGUAGE': 'pl-pl;q=0.8,pl;q=0.6,en-ZA;q=0.4,en-AU;q=0.2,de-AT;q=0.2,de;q=0.2'
        }

        base = _get_def_lang(mock_request, base_languages)
        self.assertEqual(base, base_pl)

        # 11
        mock_request.META = {
            'HTTP_ACCEPT_LANGUAGE': 'pl;q=0.8,en;q=0.6,en-ZA;q=0.4,en-AU;q=0.2,de-AT;q=0.2,de;q=0.2'
        }

        base = _get_def_lang(mock_request, base_languages)
        self.assertEqual(base, base_pl)

        # 12
        mock_request.META = {
            'HTTP_ACCEPT_LANGUAGE': 'de-zh;q=0.8,en;q=0.6,en-ZA;q=0.4,en-AU;q=0.2,de-AT;q=0.2,de;q=0.2'
        }

        base = _get_def_lang(mock_request, base_languages)
        self.assertEqual(base, base_at)

        # 13
        mock_request.META = {
            'HTTP_ACCEPT_LANGUAGE': 'es-ES'
        }

        base = _get_def_lang(mock_request, base_languages)
        self.assertEqual(base, base_gb)

    def test_interface_language_from_cookies(
        self
    ):
        mock_request = mock.MagicMock()
        mock_request.COOKIES = {
            'monster_language': 10
        }

        base_languages = []

        base_languages.extend(
            BaseLanguageFactory.create_batch(5)
        )
        base_languages = [
            BaseLanguageFactory(
                id=10,
            ),
            BaseLanguageFactory(
                id=666,
            )
        ]

        lang = landing_language(mock_request, base_languages)
        self.assertEqual(lang.id, 10)
