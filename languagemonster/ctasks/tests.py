import random
import uuid
from datetime import (
    datetime,
    timedelta,
)

import mock
import factory
from factory.fuzzy import (
    FuzzyAttribute,
    FuzzyText,
)

import unittest

from django.contrib.auth import models as contrib_models

from vocabulary.study_backend import (
    convert_to_string_array,
    get_games_played,
    get_words_to_repeat,
)
from core.models import (
    UserResult,
)

from core.mock_models import (
    MonsterUserFactory,
    LanguageFactory,
    LanguagePairFactory,
    ProgressionFactory,
    WordPairFactory,
    UserWordPairFactory,
    DS2WPFactory,
    DataSetFactory,
    UserResultFactory,
)

from utility.testing import get_random_unicode
from ctasks.game_tasks import (
    count_user_words,
    update_streak,
    compute_strength,
)

class UserStatsTest(unittest.TestCase):
    def setUp(self):
        pass

    @mock.patch('core.models.UserWordPair.objects.filter')
    @mock.patch('core.models.DS2WP.objects.filter')
    def test_count_words_user_learned(
        self,
        mock_ds2wp,
        mock_userwordpair
    ):
        user = MonsterUserFactory()

        lang1 = LanguageFactory()
        lang2 = LanguageFactory()

        lp = LanguagePairFactory(
            base_language=lang1,
            target_language=lang2
        )

        progression1 = ProgressionFactory(
            user=user,
            pair=lp
        )

        cnt = count_user_words(user, progression1)
        self.assertEqual(cnt, 0)

        wp1 = WordPairFactory(base='dog', target='pies')
        wp2 = WordPairFactory(base='cat', target='kot')
        wp3 = WordPairFactory(base='lion', target='lew')
        wp4 = WordPairFactory(base='pear', target='gruszka')

        words = [wp1, wp2, wp3]

        ds = DataSetFactory(pair=lp)

        link1 = DS2WPFactory(ds=ds, wp=wp1)
        link2 = DS2WPFactory(ds=ds, wp=wp2)
        link3 = DS2WPFactory(ds=ds, wp=wp3)
        link4 = DS2WPFactory(ds=ds, wp=wp4)

        mock_userwordpair.return_value = [
            UserWordPairFactory(user=user, word_pair=wp1, learned=True),
            UserWordPairFactory(user=user, word_pair=wp2, learned=True),
        ]
        mock_userwordpair.assert_called_with(learned=True, user=user)

        mock_ds2wp.return_value = [
            link1, link2, link3, link4
        ]

        cnt = count_user_words(user, progression1)

        self.assertEqual(cnt, 2)

    @mock.patch('core.models.UserResult.objects.filter')
    def test_compute_user_streak(
        self,
        mock_userresult,
    ):
        user = MonsterUserFactory()

        lang1 = LanguageFactory()
        lang2 = LanguageFactory()

        lp = LanguagePairFactory(
            base_language=lang1,
            target_language=lang2
        )

        progression1 = ProgressionFactory(
            user=user,
            pair=lp
        )

        # First case - no results

        mock_userresult.return_value = mock.MagicMock()
        mock_userresult.return_value.order_by.return_value = []
        # mock_userresult.assert_called_with(user=user)

        streak, avg, cnt = update_streak(
            user,
            progression1
        )

        self.assertEqual(cnt, 0)
        self.assertEqual(streak, 0)
        self.assertEqual(avg, 0)

        # Second case - a single result

        mock_userresult.return_value = mock.MagicMock()
        mock_userresult.return_value.order_by.return_value = [
            UserResultFactory(
                user=user,
                data_set=DataSetFactory(pair=lp),
                mark=50,
                date=datetime.today()
            )
        ]

        streak, avg, cnt = update_streak(
            user,
            progression1
        )

        self.assertEqual(cnt, 1)
        self.assertEqual(streak, 1)
        self.assertEqual(avg, 50)

        # Third case - several cases

        mock_userresult.return_value = mock.MagicMock()
        mock_userresult.return_value.order_by.return_value = [
            UserResultFactory(
                user=user,
                data_set=DataSetFactory(pair=lp),
                mark=60,
                date=datetime.today()
            ),
            UserResultFactory(
                user=user,
                data_set=DataSetFactory(pair=lp),
                mark=40,
                date=datetime.today() - timedelta(days=1)
            ),
            UserResultFactory(
                user=user,
                data_set=DataSetFactory(pair=lp),
                mark=80,
                date=datetime.today() - timedelta(days=2)
            )
        ]

        streak, avg, cnt = update_streak(
            user,
            progression1
        )

        self.assertEqual(cnt, 3)
        self.assertEqual(streak, 3)
        self.assertEqual(avg, 60)

        # 4th case - several cases

        mock_userresult.return_value = mock.MagicMock()
        mock_userresult.return_value.order_by.return_value = [
            UserResultFactory(
                user=user,
                data_set=DataSetFactory(pair=lp),
                mark=60,
                date=datetime.today() - timedelta(days=3)
            ),
            UserResultFactory(
                user=user,
                data_set=DataSetFactory(pair=lp),
                mark=80,
                date=datetime.today() - timedelta(days=4)
            ),
        ]

        streak, avg, cnt = update_streak(
            user,
            progression1
        )

        self.assertEqual(cnt, 2)
        self.assertEqual(streak, 0)
        self.assertEqual(avg, 70)

        # 5th case - several cases

        mock_userresult.return_value = mock.MagicMock()
        mock_userresult.return_value.order_by.return_value = [
            UserResultFactory(
                user=user,
                data_set=DataSetFactory(pair=lp),
                mark=10,
                date=datetime.today()
            ),
            UserResultFactory(
                user=user,
                data_set=DataSetFactory(pair=lp),
                mark=60,
                date=datetime.today() - timedelta(days=3)
            ),
            UserResultFactory(
                user=user,
                data_set=DataSetFactory(pair=lp),
                mark=80,
                date=datetime.today() - timedelta(days=4)
            ),
        ]

        streak, avg, cnt = update_streak(
            user,
            progression1
        )

        self.assertEqual(cnt, 3)
        self.assertEqual(streak, 1)
        self.assertEqual(avg, 50)

    def test_compute_strength(self):
        trend, new_strength = compute_strength(
            current_strength=0,
            words=0,
            streak=0,
            average=0,
            levels=0
        )

        self.assertEqual(trend, 0)
        self.assertEqual(new_strength, 0)

        trend, new_strength = compute_strength(
            current_strength=10,
            words=50, #5
            streak=0, # 0
            average=80, # 3
            levels=5 # 2
        )

        self.assertEqual(trend, 0)
        self.assertEqual(new_strength, 10)

        trend, new_strength = compute_strength(
            current_strength=50,
            words=250, #25
            streak=5, # 1
            average=75, # 3
            levels=50 # 15
        )

        self.assertEqual(trend, -1)
        self.assertEqual(new_strength, 44)

        trend, new_strength = compute_strength(
            current_strength=80,
            words=750, #75
            streak=8, # 2
            average=80, # 3
            levels=120 # 36
        )

        self.assertEqual(trend, 1)
        self.assertEqual(new_strength, 116)

