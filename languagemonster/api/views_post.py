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

class SaveResults(MonsterUserAuthView):
    def post(self, request):
        input_data = SaveResultsRequest(data=request.data)

        if not input_data.is_valid():
            logger.warning('Invalid input')

            return self.failure('Invalid input', 400)

        do_save_results(
            dataset_id=input_data.validated_data['dataset_id'],
            monster_user=self.monster_user,
            game=input_data.validated_data['game'],
            mark=input_data.validated_data['mark'],
            words_learned=input_data.validated_data['words_learned'],
            to_repeat=input_data.validated_data['to_repeat'],
        )

        return success({})

class LocalSaveResults(LocalAPIAuthView):
    def post(self, request, email):
        input_data = SaveResultsRequest(data=request.data)

        if not input_data.is_valid():
            logger.warning('Invalid input')

            return self.failure('Invalid input', 400)

        try:
            monster_user = MonsterUser.objects.get(user__email=email)
        except MonsterUser.DoesNotExist:
            return self.failure('Does not exist', 404)

        do_save_results(
            dataset_id=input_data.validated_data['dataset_id'],
            monster_user=monster_user,
            game=input_data.validated_data['game'],
            mark=input_data.validated_data['mark'],
            words_learned=input_data.validated_data['words_learned'],
            to_repeat=input_data.validated_data['to_repeat'],
        )

        return success({})

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
