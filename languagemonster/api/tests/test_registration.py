import json

from rest_framework import status
from rest_framework.test import APITestCase
from django.core.urlresolvers import reverse

from utility.testing import *

# API Tests


class TestRegistration(APITestCase):
    fixtures = ['languages.json']

    def setUp(self):
        self.conn = http_conn()
        self._test_device = get_test_device()

    def testCorrect(self):
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

        self.assertTrue(
            'api_login_hash' in data,
            'api_login_hash should be returned after successful registration'
            ' so the user can be automatically logged in'
        )

    def testPassTooShort(self):

        self.client.credentials(
            HTTP_AUTHORIZATION='Token: {token}'.format(
                token=TEST_DEVICE_KEY
            )
        )

        response = self.client.post(
            path=reverse('api:users'),
            data={
                'email': TEST_EMAIL,
                'password1': '1234567',
                'password2': '1234567',
                # TODO: language and country should be random
                'language': 'en',
                'country': 'us'
            },
        )

        data = json.loads(response.content)['data']

        self.assertEqual(response.status_code, RESP_BAD_REQ)
        self.assertEqual(data['message'], 'password_too_short')

    def testPassDontMatch(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Token: {token}'.format(
                token=TEST_DEVICE_KEY
            )
        )

        response = self.client.post(
            path=reverse('api:users'),
            data={
                'email': TEST_EMAIL,
                'password1': '87654321',
                'password2': TEST_USER_PASSWORD,
                # TODO: language and country should be random
                'language': 'en',
                'country': 'us'
            },
        )

        data = json.loads(response.content)['data']

        self.assertEqual(response.status_code, RESP_BAD_REQ)
        self.assertEqual(data['message'], 'passwords_not_equal')

    def testEmailValid(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Token: {token}'.format(
                token=TEST_DEVICE_KEY
            )
        )

        response = self.client.post(
            path=reverse('api:users'),
            data={
                'email': 'fake@email',
                'password1': TEST_USER_PASSWORD,
                'password2': TEST_USER_PASSWORD,
                # TODO: language and country should be random
                'language': 'en',
                'country': 'us'
            },
        )

        data = json.loads(response.content)['data']

        self.assertEqual(response.status_code, RESP_BAD_REQ)
        self.assertEqual(data['message'], 'email_invalid')

    def testUnique(self):
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

        self.assertEqual(response.status_code, RESP_OK)

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

        self.assertEqual(response.status_code, RESP_BAD_REQ)
        data = json.loads(response.content)['data']
        self.assertEqual(data['message'], 'email_not_unique')

    def tearDown(self):
        remove_test_data(
            device=self._test_device
        )
        # Needs to be called separately
        remove_test_user()
        self.conn.close()
