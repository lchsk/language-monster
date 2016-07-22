# -*- encoding: utf-8 -*-

import json

from core.models import *

from rest_framework import status
from rest_framework.test import APITestCase
from django.core.urlresolvers import reverse

from utility.testing import *
from utility.security import (
    create_game_session_hash,
    check_game_session
)

from api.helper.api_call import *


class TestPost(APITestCase):
    fixtures = ['languages.json', 'datasets.json', 'words.json']

    def setUp(self):

        self.conn = http_conn()
        self._test_user = get_test_user()

    def test_add_language(self):
        '''
            user starts learning a new language

            /api/users/begin
        '''

        self.client.credentials(
            HTTP_AUTHORIZATION='Token: {token}'.format(
                token=self._test_user.api_login_hash
            )
        )

        response = self.client.post(
            path=reverse('api:learn_language'),
            data={
                # TODO: make it random
                'base': 'pl',
                'target': 'en'
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = json.loads(response.content)['data']

        self.assertEqual(len(data['languages']), 1)

        user_languages = Progression.objects.filter(user=self._test_user)

        self.assertEqual(len(user_languages), 1)
        self.assertEqual(
            user_languages[0].pair.base_language.acronym,
            'pl'
        )
        self.assertEqual(
            user_languages[0].pair.target_language.acronym,
            'en'
        )

    def test_save_results_js(self):
        """
            save user's results (from JS)

            POST /api/users/results/js
        """

        d = get_random_dataset()

        game_session_id = create_game_session_hash(
            self._test_user,
            d
        )

        self._add_word_pairs(dataset=d)

        self.client.credentials(
            HTTP_AUTHORIZATION='Token: {token}'.format(
                token=self._test_user.api_login_hash
            )
        )

        response = self.client.post(
            path=reverse('api:results_js'),
            data={
                'game_session_id': game_session_id,
                'dataset_id': d.id,
                'email': TEST_EMAIL,
                'mark': -100,
                'words_learned': self.words_learned,
                'to_repeat': self.to_repeat,
                'game': 'simple'
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            check_game_session(game_session_id),
            True
        )
        self._check_results_were_saved(dataset=d)

    def test_save_results(self):
        """
            save user's results

            POST /api/users/results
        """

        d = get_random_dataset()

        self._add_word_pairs(dataset=d)

        # game_session_id = create_game_session_hash(
        #     self._test_user,
        #     d
        # )

        self.client.credentials(
            HTTP_AUTHORIZATION='Token: {token}'.format(
                token=self._test_user.api_login_hash
            )
        )

        response = self.client.post(
            path=reverse('api:results'),
            data={
                # 'game_session_id': game_session_id,
                'dataset_id': d.id,
                'email': TEST_EMAIL,
                'mark': -100,
                'words_learned': self.words_learned,
                'to_repeat': self.to_repeat,
                'game': 'simple'
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self._check_results_were_saved(dataset=d)

    def _add_word_pairs(self, dataset):
        """
            Helper
        """

        links = DS2WP.objects.filter(ds=dataset)

        self.words_learned = [
            [link.wp.base, link.wp.target]
            for link in links[:5]
        ]

        self.to_repeat = [
            [link.wp.base, link.wp.target]
            for link in list(reversed(links))[:5]
        ]

    def _check_results_were_saved(self, dataset):
        """
            Helper
            Should be called from testSaveResults or testSaveResultsJS
        """

        games_played = MonsterUserGame.objects.filter(
            monster_user=self._test_user
        )

        self.assertEqual(len(games_played), 1)
        self.assertEqual(games_played[0].game, 'simple')

        ur = UserResult.objects.filter(user=self._test_user)
        self.assertEqual(len(ur), 1)
        self.assertEqual(ur[0].data_set, dataset)
        self.assertEqual(ur[0].game, 'simple')
        self.assertEqual(ur[0].mark, -100)

        # TODO: We should test Progression but
        # it's needs a separate call to add
        # p = Progression.objects(user=self._test_user)
        # self.assertEqual(len(p), 1)

        user_word_pairs = UserWordPair.objects.filter(user=self._test_user)

        self.assertEqual(len(user_word_pairs), 10)

        learned = []
        repeat = []

        for wp in user_word_pairs:

            if wp.learned:
                learned.append([wp.word_pair.base, wp.word_pair.target])
            elif wp.repeat:
                repeat.append([wp.word_pair.base, wp.word_pair.target])

        self.assertEqual(
            sorted(learned), sorted(self.words_learned)
        )

        self.assertEqual(
            sorted(repeat), sorted(self.to_repeat)
        )

    def tearDown(self):
        remove_test_data(user=self._test_user)
        self.conn.close()

# # {
# # "dataset_id": "5521b4ec6e8ee52109857793",
# # "email":"mjlechowski@gmail.com",
# # "mark":98,
# # "words_learned":[
# #            ["cat", "gato"]
# # ],
# # "to_repeat":[]
# # }
