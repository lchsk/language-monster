import logging

from core.models import MonsterUser

from utility.exception import MonsterException

from vocabulary.impl.study import do_save_results

from api.views.base import (
    MonsterUserAuthView,
    PublicAPIAuthView,
)

from api.serializers import (
    SaveResultsRequest,
    SaveResultsJSRequest,
)

logger = logging.getLogger(__name__)

class SaveResults(MonsterUserAuthView):
    def post(self, request):
        input_data = SaveResultsRequest(data=request.data)

        if not input_data.is_valid():
            logger.warning('Invalid input')

            return self.failure('Invalid input', 400)

        try:
            do_save_results(
                dataset_id=input_data.validated_data['dataset_id'],
                monster_user=self.monster_user,
                game=input_data.validated_data['game'],
                mark=input_data.validated_data['mark'],
                words_learned=input_data.validated_data['words_learned'],
                to_repeat=input_data.validated_data['to_repeat'],
            )
        except MonsterException as e:
            logger.info('Saving results failed: %s', e)

            return self.failure('Internal error', 500)

        return self.success({})


class LocalSaveResults(PublicAPIAuthView):
    def post(self, request):
        input_data = SaveResultsJSRequest(data=request.data)

        if not input_data.is_valid():
            logger.warning('Invalid input')

            return self.failure('Invalid input', 400)

        try:
            monster_user = MonsterUser.objects.get(
                uri=input_data.validated_data['email']
            )
        except MonsterUser.DoesNotExist:
            return self.failure('Does not exist', 404)

        try:
            do_save_results(
                dataset_id=input_data.validated_data['dataset_id'],
                monster_user=monster_user,
                game=input_data.validated_data['game'],
                mark=input_data.validated_data['mark'],
                words_learned=input_data.validated_data['words_learned'],
                to_repeat=input_data.validated_data['to_repeat'],
            )
        except MonsterException as e:
            logger.info('Saving results failed: %s', e)

            return self.failure('Internal error', 500)

        return self.success({})
