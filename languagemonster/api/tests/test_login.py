import json
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.urlresolvers import reverse

from utility.testing import *


class TestLogin(APITestCase):

    fixtures = ['languages.json']

    def setUp(self):

        self.conn = http_conn()
        self._test_device = get_test_device()

        self.client.credentials(
            HTTP_AUTHORIZATION='Token: {token}'.format(
                token=TEST_DEVICE_KEY
            )
        )

        response = self.client.post(
            path=reverse('api:users'),
            data={
                'email': TEST_EMAIL,
                'password1': TEST_USER_PASSWORD,
                'password2': TEST_USER_PASSWORD,
                # TODO: language and country should be random
                'language': 'en',
                'country': 'us'
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)['data']
        self._hash1 = data['api_login_hash']

    def testCorrectLoginData(self):

        self.client.credentials(
            HTTP_AUTHORIZATION='Token: {token}'.format(
                token=TEST_DEVICE_KEY
            )
        )

        response = self.client.put(
            path=reverse('api:users'),
            data={
                'email': TEST_EMAIL,
                'password': TEST_USER_PASSWORD
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = json.loads(response.content)['data']

        self.assertTrue(
            'api_login_hash' in data,
            'api_login_hash should be returned after successful registration'
            ' so the user can be automatically logged in'
        )

        hash2 = data['api_login_hash']

        self.assertNotEqual(
            self._hash1,
            hash2
        )

    def testWrongPassword(self):

        self.client.credentials(
            HTTP_AUTHORIZATION='Token: {token}'.format(
                token=TEST_DEVICE_KEY
            )
        )

        response = self.client.put(
            path=reverse('api:users'),
            data={
                'email': TEST_EMAIL,
                'password': '123456789'
            },
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def tearDown(self):
        remove_test_data(
            device=self._test_device,
        )
        # Needs to be called separately
        remove_test_user()
        self.conn.close()
