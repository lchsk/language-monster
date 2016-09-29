import logging

from core.models import Progression
from core.data.base_language import BASE_LANGUAGES
from core.data.language_pair import LANGUAGE_PAIRS_FLAT

from api.serializers import (
    StartLearningLanguageRequest,
    LanguagePairSerializer,
    BaseLanguageSerializer,
)

from api.views.base import (
    APIAuthView,
    MonsterUserAuthView,
)

logger = logging.getLogger(__name__)

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


class LanguagesToLearn(APIAuthView):
    def get(self, request):
        resp = LanguagePairSerializer(
            LANGUAGE_PAIRS_FLAT.values(),
            many=True,
        )

        return self.success(resp.data)


class Languages(APIAuthView):
    def get(self, request):
        resp = BaseLanguageSerializer(
            BASE_LANGUAGES.values(),
            many=True,
        )

        return self.success(resp.data)
