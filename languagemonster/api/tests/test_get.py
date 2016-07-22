import json

from django.core.urlresolvers import reverse
from django.conf import settings
from rest_framework import status
from rest_framework.test import APITestCase

# from django.test import TestCase
# from django.conf import settings
from core.models import *
from utility.testing import (
    TEST_DEVICE_KEY,
    TEST_EMAIL,
    # AUTH_API_KEY,
    get_test_device,
    get_test_user,
    get_random_dataset,
    remove_test_data,
    http_conn,
)
from api.helper.api_call import *


class TestGet(APITestCase):

    fixtures = ['languages.json', 'datasets.json', 'words.json']

    def setUp(self):

        self.conn = http_conn()
        self._test_device = get_test_device()
        self._test_user = get_test_user()

    def testLanguages(self):
        """
            general information about languages

            GET /languages
        """

        self.client.credentials(
            HTTP_AUTHORIZATION='Token: {token}'.format(
                token=TEST_DEVICE_KEY
            )
        )

        response = self.client.get(
            path=reverse('api:languages'),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def testLanguagePairs(self):
        """
            languages pairs (languages users can learn)

            GET /languages/pairs
        """

        self.client.credentials(
            HTTP_AUTHORIZATION='Token: {token}'.format(
                token=TEST_DEVICE_KEY
            )
        )

        response = self.client.get(
            path=reverse('api:language_pairs'),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        pairs = json.loads(response.content)

        # Make sure only visible Language Pairs are returned

        for pair in pairs['data']:
            base = pair['base_language']['acronym']
            target = pair['target_language']['acronym']

            self.assertNotEqual(base, '')
            self.assertNotEqual(target, '')

            base_obj = Language.objects.filter(acronym=base).first()
            target_obj = Language.objects.filter(acronym=target).first()

            self.assertIsNotNone(base_obj)
            self.assertIsNotNone(target_obj)

            pair_obj = LanguagePair.objects.filter(
                base_language=base_obj,
                target_language=target_obj
            ).first()

            self.assertIsNotNone(pair_obj)
            self.assertTrue(pair_obj.visible)

    def testUserStats(self):
        """
            receives user's statistics

            /api/users/<email>/stats
        """

        self.client.credentials(
            HTTP_AUTHORIZATION='Token: {token}'.format(
                token=self._test_user.api_login_hash
            )
        )

        response = self.client.get(
            path=reverse('api:user_stats', args=[self._test_user.user.email]),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Expected to be empty first

        pair = LanguagePair.objects.first()
        p = Progression(user=self._test_user, pair=pair)
        p.save()

        self.client.credentials(
            HTTP_AUTHORIZATION='Token: {token}'.format(
                token=self._test_user.api_login_hash
            )
        )

        response = self.client.get(
            path=reverse('api:user_stats', args=[self._test_user.user.email]),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # remove

        p.delete()

    def testGames(self):
        '''
            list of available games

            GET /api/games
        '''

        self.client.credentials(
            HTTP_AUTHORIZATION='Token: {token}'.format(
                token=TEST_DEVICE_KEY
            )
        )

        response = self.client.get(
            path=reverse('api:games'),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def testPing(self):
        '''
            ping

            GET /api/ping
        '''

        self.client.credentials(
            HTTP_AUTHORIZATION='Token: {token}'.format(
                token=settings.API_KEY
            )
        )

        response = self.client.get(
            path=reverse('api:ping'),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def testGetUser(self):
        '''
            returns user profile

            GET /api/users/<email>
        '''

        self.client.credentials(
            HTTP_AUTHORIZATION='Token: {token}'.format(
                token=self._test_user.api_login_hash
            )
        )

        response = self.client.get(
            path=reverse(
                'api:get_or_update_user',
                args=[self._test_user.user.email]
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def testPasswordRecovery(self):
        '''
            get new password

            GET /api/users/<email>/password
        '''

        self.client.credentials(
            HTTP_AUTHORIZATION='Token: {token}'.format(
                token=TEST_DEVICE_KEY
            )
        )

        response = self.client.get(
            path=reverse(
                'api:password',
                args=[self._test_user.user.email]
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def testGetDatasets(self):
        """
            datasets available for a language pair

            /api/data/<base>/<target>
        """

        self.client.credentials(
            HTTP_AUTHORIZATION='Token: {token}'.format(
                token=TEST_DEVICE_KEY
            )
        )

        response = self.client.get(
            path=reverse(
                'api:datasets',
                # FIXME
                args=['pl', 'en']
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def testGetData(self):
        """
            returns words from a datset prepared for a specific user

            /api/data/<dataset_id>/<email>

            (it calls /api/get-game-data)
        """

        d = get_random_dataset()

        self.client.credentials(
            HTTP_AUTHORIZATION='Token: {token}'.format(
                token=self._test_user.api_login_hash
            )
        )

        response = self.client.get(
            path=reverse(
                'api:data',
                # FIXME
                args=[d.id, TEST_EMAIL]
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def tearDown(self):
        remove_test_data(
            device=self._test_device,
            user=self._test_user
        )
        self.conn.close()
