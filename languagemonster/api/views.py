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
from vocabulary.impl.study import *

from core.data.base_language import BASE_LANGUAGES

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



from django.http import Http404
# from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from api.views2.base import *

class UserRegistration(APIAuthView):
    def post(self, request):
        input_data = UserRegistrationRequest(data=request.data)

        if not input_data.is_valid():
            logger.warning('Invalid input')

            return self.failure('Invalid input', 400)

        base_language = input_data.validated_data['base_language']

        if base_language not in BASE_LANGUAGES:
            return self.failure('Invalid base language', 400)

        result, error_code, error_str = register(
            email=input_data.validated_data['email'],
            password1=input_data.validated_data['password'],
            password2=input_data.validated_data['password'],
            confirmation_required=False,
            base_language=BASE_LANGUAGES[base_language],
        )

        if result:
            return self.success({})
        else:
            return self.failure(error_code)


class UserLogin(APIAuthView):
    def post(self, request):
        input_data = UserLoginRequest(data=request.data)

        if not input_data.is_valid():
            logger.warning('Invalid input')

            return self.failure('Invalid input', 400)

        user = authenticate_user(
            email=input_data['email'].value,
            password=input_data['password'].value,
            new_hash=True,
        )

        if not user:
            logger.warning('Invalid email or password')

            return self.failure('Invalid email or password', 401)

        logger.info('Login successful: {}'.format(input_data['email']))

        resp = UserLoginResponse(data=dict(login_hash=user.api_login_hash))

        if not resp.is_valid():
            logger.warning('Internal error')

            return self.failure('Internal error', 500)

        return self.success(resp.data)



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
