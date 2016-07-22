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

from vocabulary.study_backend import (
    convert_to_string_array,
    get_games_played,
    get_words_to_repeat,
)
from core.models import (
    Language,
    BaseLanguage,
    WordPair,
    UserWordPair,
    MonsterUser,
    MonsterUserGame,
)

class VocabularyPresentationTest(unittest.TestCase):
    def setUp(self):
        pass

    @mock.patch('core.models.MonsterUserGame.objects.filter')
    def test_user_played_games_are_read_success(self, mock_monster_user):
        mock_games = ['game1', 'game2', 'game3']

        user = MonsterUserFactory()

        monster_user_games = []

        monster_user_games.extend(
            MonsterUserGameFactory.create_batch(5)
        )
        monster_user_games2 = [
            MonsterUserGameFactory(
                monster_user=user,
                game='game1'
            ),
            MonsterUserGameFactory(
                monster_user=user,
                game='game2'
            )
        ]

        mock_monster_user.return_value = monster_user_games2
        games_played = get_games_played(user)

        for m in games_played:
            self.assertEqual(m in ['game1', 'game2'], True)

    def test_word_pairs_serialized_for_games_empty(self):
        self.assertEqual(
            convert_to_string_array([]),
            []
        )

    def test_word_pairs_serialized_for_games_success(self):
        # all_word_pairs = WordPair.objects.all()
        # random_len = random.randint(1, 10)
        # 
        # random_word_pairs = [
        #     random.choice(all_word_pairs)
        #     for _ in xrange(random_len)
        # ]
        random_word_pairs = []
        random_word_pairs.extend(
            WordPairFactory.create_batch(
                random.randint(1, 10)
            )
        )

        for word_pair in random_word_pairs:
            self.assertIsInstance(word_pair, WordPair)

        converted_words = convert_to_string_array(random_word_pairs)

        for word_pair in converted_words:
            self.assertIsInstance(word_pair, list)
            self.assertEqual(len(word_pair), 2)

        for list_repr, obj_repr in zip(converted_words, random_word_pairs):
            self.assertEqual(list_repr[0], obj_repr.base)
            self.assertEqual(list_repr[1], obj_repr.target)

    @mock.patch('core.models.UserWordPair.objects.filter')
    def test_words_to_be_repeated_are_from_same_dataset(
        self,
        mock_return
    ):

        user = MonsterUserFactory()

        wp1 = WordPairFactory(base='dog', target='pies')
        wp2 = WordPairFactory(base='cat', target='kot')
        wp3 = WordPairFactory(base='lion', target='lew')
        wp4 = WordPairFactory(base='pear', target='gruszka')

        # Only from a single data set
        words = [wp1, wp2, wp3]

        mock_return.return_value = [
            UserWordPairFactory(user=user, word_pair=wp1),
            UserWordPairFactory(user=user, word_pair=wp2),
            UserWordPairFactory(user=user, word_pair=wp3),
            UserWordPairFactory(user=user, word_pair=wp4),
        ]

        to_repeat = get_words_to_repeat(user, words)

        self.assertEqual(len(to_repeat), 3)

        for wp in to_repeat:
            self.assertEqual(wp in words, True)
