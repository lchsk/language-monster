from rest_framework import status
from rest_framework.test import APITestCase
from django.core.urlresolvers import reverse
import json
from core.models import *

from utility.testing import *
from api.helper.api_call import *


class TestPut(APITestCase):
    fixtures = ['languages.json', 'datasets.json']

    def setUp(self):

        self.conn = http_conn()
        self._test_user = get_test_user()

    def testUpdateUserProfile(self):

        new_first_name = 'Thomas'
        new_last_name = 'Jefferson'

        self.assertNotEqual(
            self._test_user.user.first_name,
            new_first_name
        )

        self.assertNotEqual(
            self._test_user.user.last_name,
            new_last_name
        )

        self.client.credentials(
            HTTP_AUTHORIZATION='Token: {token}'.format(
                token=self._test_user.api_login_hash
            )
        )

        response = self.client.put(
            path=reverse(
                'api:get_or_update_user',
                args=[self._test_user.user.email]
            ),
            data={
                'first_name': new_first_name,
                'last_name': new_last_name
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = json.loads(response.content)['data']
        self.assertEqual(data['first_name'], new_first_name)
        self.assertEqual(data['last_name'], new_last_name)

    def testSetBannedGames(self):
        '''
            set games the user does not want to play

            PUT /api/users/games
        '''

        user_games = MonsterUserGame.objects.filter(
            monster_user=self._test_user
        )

        self.assertEqual(len(user_games), 0)

        self.client.credentials(
            HTTP_AUTHORIZATION='Token: {token}'.format(
                token=self._test_user.api_login_hash
            )
        )

        response = self.client.put(
            path=reverse('api:banned_games'),
            data={
                # FIXME: make it random
                'banned': ['simple']
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)['data']

        self.assertEqual(len(data['banned_games']), 1)
        self.assertEqual(data['banned_games'][0]['game'], 'simple')

    def testSetLanguage(self):
        '''
            set user's interface language (current_language/base_language)

            PUT /api/users/language
        '''

        self.client.credentials(
            HTTP_AUTHORIZATION='Token: {token}'.format(
                token=self._test_user.api_login_hash
            )
        )

        response = self.client.put(
            path=reverse('api:user_language'),
            data={
                # FIXME: make it random
                'language': 'en',
                'country': 'NZ'
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = json.loads(response.content)['data']

        self.assertEqual(
            data['base_language']['country'],
            'nz'
        )

        self.assertEqual(
            data['current_language']['acronym'],
            'en'
        )

    def testChangeUserEmail(self):
        '''
            change user's email

            PUT /api/users/email
        '''

        self.assertEqual(self._test_user.user.email, TEST_EMAIL)

        new_email = 'bugsbunny@language-monster.com'

        self.client.credentials(
            HTTP_AUTHORIZATION='Token: {token}'.format(
                token=self._test_user.api_login_hash
            )
        )

        response = self.client.put(
            path=reverse('api:user_email'),
            data={
                'email': new_email,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        test_user_reloaded = MonsterUser.objects.filter(
            user__email=self._test_user.user.email
        ).first()

        self.assertEqual(
            test_user_reloaded.new_email,
            new_email
        )

        self.assertNotEqual(
            test_user_reloaded.user.email,
            new_email
        )

    def tearDown(self):
        remove_test_data(
            user=self._test_user
        )
        self.conn.close()
