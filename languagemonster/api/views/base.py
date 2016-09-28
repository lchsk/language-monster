import logging

from django.conf import settings

from core.models import MonsterUser

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.views import APIView
from rest_framework.response import Response

logger = logging.getLogger(__name__)

class BaseAPIAuth(BaseAuthentication):
    def authenticate(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')

        if token is None:
            logger.warning('No token found')
            raise AuthenticationFailed('Unauthorised')

        logger.info('Token found')

        self._token = token


class LocalAPIAuth(BaseAuthentication):
    def authenticate(self, request):
        remote_addr = request.META.get('REMOTE_ADDR')

        if remote_addr not in settings.LOCAL_API_HOSTS:
            logger.warning('Remote address not localhost: %s' % remote_addr)

            raise AuthenticationFailed('Unauthorised')

        logger.info('Remote address is local: %s' % remote_addr)


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

############################################
#                                          #
#           Authorisation classes          #
#                                          #
############################################

class MonsterUserAuth(BaseAPIAuth):
    def authenticate(self, request):
        super(MonsterUserAuth, self).authenticate(request)

        monster_user = MonsterUser.objects.filter(
            api_login_hash=self._token
        )

        if len(monster_user) != 1:
            logger.warning('Monster User not found')

            raise AuthenticationFailed('Unauthorised')

        logger.info('Monster User authenticated, id: %s' % monster_user.id)

        return monster_user.first(), None

class APIAuth(BaseAPIAuth):
    def authenticate(self, request):
        super(APIAuth, self).authenticate(request)

        if self._token != settings.API_KEY:
            logger.warning('Token invalid')

            raise AuthenticationFailed('Unauthorised')

        logger.info('Token valid')

############################################
#                                          #
#      View - use this as base class       #
#                                          #
############################################

class APIAuthView(APIView, BaseView):
    authentication_classes = (APIAuth,)

class LocalAPIAuthView(APIView, BaseView):
    authentication_classes = (LocalAPIAuth,)

class MonsterUserAuthView(APIView, BaseView):
    authentication_classes = (MonsterUserAuth,)

    @property
    def monster_user(self):
        return self.request.user
