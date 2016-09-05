from django.conf import settings

from core.models import MonsterUser

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.views import APIView
from rest_framework.response import Response

class BaseAPIAuth(BaseAuthentication):
    def authenticate(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')

        if token is None:
            raise AuthenticationFailed('Unauthorised')

        self._token = token

class BaseView(object):
    def success(self, data):
        return Response(dict(
            status='success',
            data=data,
        ), 200)

    def failure(self, data, code=400):
        return Response(dict(
            status='failure',
            data=data,
        ), code)

class MonsterUserAuth(BaseAPIAuth):
    def authenticate(self, request):
        super(MonsterUserAuth, self).authenticate(request)

        monster_user = MonsterUser.objects.filter(
            api_login_hash=self._token
        )

        if len(monster_user) != 1:
            raise AuthenticationFailed('Unauthorised')

class APIAuth(BaseAPIAuth):
    def authenticate(self, request):
        super(APIAuth, self).authenticate(request)

        if self._token != settings.API_KEY:
            raise AuthenticationFailed('Unauthorised')

class APIAuthView(APIView, BaseView):
    authentication_classes = (APIAuth,)

class MonsterUserAuthView(APIView, BaseView):
    authentication_classes = (MonsterUserAuth,)
