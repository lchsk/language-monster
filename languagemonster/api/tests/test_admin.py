from django.conf import settings
from core.models import *

from utility.testing import *
from api.helper.api_call import *
from api.helper.calls import CALLS
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.urlresolvers import reverse


class TestDocs(APITestCase):
    def test_print_docs(self):

        for k, v in CALLS.iteritems():
            print v.url


class TestAdmin(APITestCase):
    def setUp(self):

        self.conn = http_conn()

    def test_device_registration(self):
        """
            register new device

            /devices
        """

        self.client.credentials(
            HTTP_AUTHORIZATION='Token: {token}'.format(
                token=settings.API_KEY
            )
        )

        response = self.client.post(
            path=reverse('api:devices'),
            data={
                'os': TEST_OS,
                'model': 'iphone 17',
                'sdk': '13.5',
                'device': 'super iphone',
                'manufacturer': 'Apple'
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def tearDown(self):
        remove_test_data()
        self.conn.close()
