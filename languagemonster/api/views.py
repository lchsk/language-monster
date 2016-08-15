import json

from django.conf import settings

import views_get
import views_put
from django.core.urlresolvers import reverse
from api.helper.api_call import *
from core.models import *
from core.impl.user import *
from models import *
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from serializers import *
from utility.api_utils import validate
from utility.interface import *
from vocabulary.study_backend import *

logger = logging.getLogger(__name__)
settings.LOGGER(logger, settings.LOG_API_HANDLER)


def link_user_device(user, device):
    """
        assigns user to a device
    """

    if user and device:
        if not device.user:
            device.user = user
            device.save()


@validate('POST /api/users')
def user_register(request, *args, **kwargs):
    """
        method actually doing registration for the API call
    """

    serializer = UserRegistrationSerializer(data=request.data)

#  and serializer.validate_keys()
    if serializer.is_valid():

        base_language = BaseLanguage.objects.filter(
            country=request.data['country']
        ).first()

        # import pdb
        # pdb.set_trace()

        result, error_code, error_str = register(
            serializer['email'].value,
            serializer['password1'].value,
            serializer['password2'].value,
            True,
            base_language
        )

        if result:
            u = MonsterUser.objects.filter(
                user__email=serializer['email'].value
            ).first()

            if not u:
                return error(
                    RESP_SER_ERR,
                    "Error writing new user to database"
                )

            link_user_device(u, kwargs.get('AUTHORIZED_CONTENT', None))

            user_serializer_url(u)

            u.languages = Progression.objects.filter(
                user=u
            )
            u.banned_games = MonsterUserGame.objects.filter(
                monster_user=u,
                banned=True
            )
            u.games_played = MonsterUserGame.objects.filter(
                monster_user=u,
                played=True
            )

            user_json = BaseUserSerializerWithLoginHash(u)

            return success(user_json.data)
        else:
            return error(RESP_BAD_REQ, str(error_code))

    return error(RESP_BAD_REQ, str(e.errors))


@validate('PUT /api/users')
def user_login(request, *args, **kwargs):

    serializer = UserLoginSerializer(data=request.data)

    if serializer.is_valid():

        user = authenticate_user(
            email=serializer['email'].value,
            password=serializer['password'].value,
            new_hash=True
        )

        if not user:
            logger.debug(
                "Invalid credentials for email: %s",
                serializer['email'].value
            )
            return error(RESP_UNAUTH, "Invalid credentials")

        # mu = MonsterUser.objects.filter(user=user).first()

        link_user_device(user, kwargs.get('AUTHORIZED_CONTENT', None))

        user_serializer_url(user)

        # TODO: find better way to fill MonsterUser with banned/played games
        user.languages = Progression.objects.filter(
            user=user
        )
        user.banned_games = MonsterUserGame.objects.filter(
            monster_user=user,
            banned=True
        )
        user.games_played = MonsterUserGame.objects.filter(
            monster_user=user,
            played=True
        )

        ret_json = BaseUserSerializerWithLoginHash(user)

        return success(ret_json.data)

    return error(RESP_BAD_REQ, str(serializer.errors))


@api_view(['POST', 'PUT'])
def users(request, *args, **kwargs):
    """
        POST - registration
        PUT - login
    """

    if request.method == METHOD_POST:

        # registration

        return user_register(request)

    elif request.method == METHOD_PUT:

        # login

        return user_login(request)


@api_view(['GET', 'PUT'])
def get_or_update_user(request, email, *args, **kwargs):
    """ Update a user (PUT) or get (GET)."""

    if request.method == METHOD_PUT:
        return views_put.update_user(request, email, *args, **kwargs)
    elif request.method == METHOD_GET:
        return views_get.get_user(request, email, *args, **kwargs)
    return error(RESP_METHOD_NOT_ALLOWED, "Method not allowed")


@api_view(['GET'])
def get_game_data(request, dataset_id, email):
    """JS games only.

    """

    # TODO: Check if this is used by js games or other parts except for the API
    if request.method == METHOD_GET:
        # d = DataSet.objects.filter(id=dataset_id).first()
        u = MonsterUser.objects.filter(user__email=email).first()

        if not u:
            print 'User/dataset not found'
            return Response({}, status=status.HTTP_404_NOT_FOUND)

        # return a list of game data items

        list_of_sets = []

        # Get data for several levels at once
        # for i in xrange(sets):
        #     include_words_to_repeat = (i == 0)
            # list_of_sets.append(
        list_of_sets = game_data(
            dataset_id=dataset_id,
            user=u,
            max_rounds=settings.GAMES_DEFAULT_WORDS_COUNT,
            to_json=False,
            include_words_to_repeat=True,
            number_of_sets=settings.GAMES_DEFAULT_WORD_SETS_COUNT
        )

        return Response(json.dumps(list_of_sets), status=status.HTTP_200_OK)

    return Response({}, status=status.HTTP_400_BAD_REQUEST)
