import logging
from collections import namedtuple

from core.models import (
    DataSet,
    MonsterUser,
)
from core.data.language_pair import LANGUAGE_PAIRS

from vocabulary.impl.study import (
    get_game_words,
    get_datasets_by_base,
)

from api.serializers import (
    DataSetSerializer,
    ToStudySerializer,
    GetWordsFilters,
    GetWordsSingleSetSerializer,
)

from api.views.base import (
    APIAuthView,
    PublicAPIAuthView,
    MonsterUserAuthView,
)

logger = logging.getLogger(__name__)

ToStudy = namedtuple('ToStudy', 'langs_to_learn datasets')

class LocalGetToStudy(PublicAPIAuthView):
    def get(self, request, language):
        langs_to_learn = LANGUAGE_PAIRS[language]

        datasets = get_datasets_by_base(language)

        resp = ToStudySerializer(ToStudy(
            langs_to_learn=langs_to_learn.values(),
            datasets=datasets,
        ))

        return self.success(resp.data)


class AvailableDatasets(APIAuthView):
    def get(self, request, lang_pair):
        # TODO: Use get_datasets (vocabulary.impl.study)
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


class LocalGetWords(PublicAPIAuthView):
    def get(self, request, dataset_id, uri):
        filters = GetWordsFilters(data=self.request.query_params)

        if not filters.is_valid():
            logger.warning('Invalid filters')

            return self.failure('Invalid input', 400)

        try:
            monster_user = MonsterUser.objects.get(uri=uri)
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
