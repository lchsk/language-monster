import logging

from django.conf import settings

from core.models import (
    DataSet,
    MonsterUser,
)

from vocabulary.impl.study import get_game_words

from api.serializers import (
    DataSetSerializer,
    GetWordsFilters,
    GetWordsSingleSetSerializer,
)

from api.views.base import (
    APIAuthView,
    LocalAPIAuthView,
    MonsterUserAuthView,
)

logger = logging.getLogger(__name__)

class AvailableDatasets(APIAuthView):
    def get(self, request, lang_pair):
        datasets = DataSet.objects.filter(
            lang_pair=lang_pair,
            visible=True,
            status='A',
        )

        resp = DataSetSerializer(datasets, many=True)

        return self.success(resp.data)


class GetWords(MonsterUserAuthView):
    def get(self, request, dataset_id):
        filters = GetWordsFilters(data=self.request.query_params)

        if not filters.is_valid():
            logger.warning('Invalid filters')

            return self.failure('Invalid input', 400)

        words = get_game_words(
            dataset_id=dataset_id,
            monster_user=self.monster_user,
            rounds=filters.validated_data['rounds'],
            include_words_to_repeat=True,
            nsets=filters.validated_data['sets'],
        )

        resp = GetWordsSingleSetSerializer(data=words, many=True)

        if not resp.is_valid():
            logger.warning('Invalid words serialization')

            return self.failure('Invalid words serialization', 500)

        return self.success(resp.data)


class LocalGetWords(LocalAPIAuthView):
    def get(self, request, dataset_id, email):
        filters = GetWordsFilters(data=self.request.query_params)

        if not filters.is_valid():
            logger.warning('Invalid filters')

            return self.failure('Invalid input', 400)

        try:
            monster_user = MonsterUser.objects.get(user__email=email)
        except MonsterUser.DoesNotExist:
            return self.failure('Does not exist', 404)

        words = get_game_words(
            dataset_id=dataset_id,
            monster_user=monster_user,
            rounds=filters.validated_data['rounds'],
            include_words_to_repeat=True,
            nsets=filters.validated_data['sets'],
        )

        resp = GetWordsSingleSetSerializer(data=words, many=True)

        if not resp.is_valid():
            logger.warning('Invalid words serialization')

            return self.failure('Invalid words serialization', 500)

        return self.success(resp.data)
