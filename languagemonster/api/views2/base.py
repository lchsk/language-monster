from django.conf import settings

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.views import APIView

class BaseAPIAuth(BaseAuthentication):
    def authenticate(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')

        if token is None:
            raise AuthenticationFailed('Unauthorised')

        self._token = token

class APIAuth(BaseAPIAuth):
    def authenticate(self, request):
        super(APIAuth, self).authenticate(request)

        if self._token != settings.API_KEY:
            raise AuthenticationFailed('Unauthorised')

class APIAuthView(APIAuth, APIView):
    authentication_classes = (APIAuth,)
