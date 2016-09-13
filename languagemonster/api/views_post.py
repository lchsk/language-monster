import logging

from serializers import *
from rest_framework.decorators import api_view
from models import *
from core.models import *
from core.impl.user import *
from vocabulary.impl.study import *
from django.conf import settings
from django.core.urlresolvers import reverse

from api.helper.api_call import *
from utility.api_utils import validate

logger = logging.getLogger(__name__)
settings.LOGGER(logger, settings.LOG_API_HANDLER)

from django.http import Http404
# from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from api.views2.base import *

def _save_results(request, serializer_cls, *args, **kwargs):
    if request.method == METHOD_POST:
        serializer = serializer_cls(data=request.data)

        if serializer.is_valid():
            user = MonsterUser.objects.filter(
                user__email=serializer['email'].value
            ).first()
            dataset = DataSet.objects.filter(
                id=serializer['dataset_id'].value
            ).first()

            if not all((user, dataset)):
                return error(RESP_NOT_FOUND, "")

            if serializer.validated_data.get('game_session_id'):
                dataset_id = serializer['game_session_id'].value
            else:
                dataset_id = serializer['dataset_id'].value

            game = serializer['game'].value
            mark = serializer['mark'].value
            words_learned = serializer['words_learned'].value
            to_repeat = serializer['to_repeat'].value

            do_save_results(
                dataset_id=serializer['dataset_id'].value,
                dataset=dataset,
                email=serializer['email'].value,
                user=user,
                game=game,
                mark=mark,
                words_learned=words_learned,
                to_repeat=to_repeat
            )

            return success({})
        else:
            return error(RESP_BAD_REQ, str(serializer.errors))

    return error(RESP_BAD_REQ, "Invalid input data")


@api_view(['POST'])
@validate('POST /api/users/results')
def save_results(request, *args, **kwargs):
    """
        receives single game results
    """

    return _save_results(
        request,
        ResultsSubmitRequest,
        *args,
        **kwargs
    )


@api_view(['POST'])
def save_results_js(request, *args, **kwargs):

    return _save_results(
        request,
        ResultsSubmitRequest,
        *args,
        **kwargs
    )



class StartLearningLanguage(MonsterUserAuthView):
    def post(self, request):
        input_data = StartLearningLanguageRequest(data=request.data)

        if not input_data.is_valid():
            logger.warning('Invalid input')

            return self.failure('Invalid input', 400)

        progressions = Progression.objects.filter(
            user=self.monster_user,
            lang_pair=input_data.validated_data['lang_pair'],
        )

        if len(progressions) != 0:
            logger.warning('{} already learning {}'.format(
                self.monster_user,
                input_data.validated_data['lang_pair'],
            ))

            return self.failure('Already learning', 400)

        progression = Progression(
            user=self.monster_user,
            lang_pair=input_data.validated_data['lang_pair'],
        )

        progression.save()

        return self.success({})
