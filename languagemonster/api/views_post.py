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
        ResultsWithGameSessionSubmitRequest,
        *args,
        **kwargs
    )


@api_view(['POST'])
@validate('POST /api/users/begin')
def add_language(request, *args, **kwargs):
    """
        users starts learning a new language
    """

    if request.method == METHOD_POST:

        user = kwargs['AUTHORIZED_CONTENT']

        if not user:
            return error(RESP_UNAUTH, "Invalid token")

        b = Language.objects.filter(acronym=request.data['base']).first()
        t = Language.objects.filter(acronym=request.data['target']).first()

        if not b or not t:
            return error(RESP_NOT_FOUND, "{0} or {1} does not exist".format(
                request.data['base']),
                request.data['target']
            )

        pair = LanguagePair.objects.filter(
            base_language=b,
            target_language=t
        ).first()

        if not pair:
            return error(
                RESP_NOT_FOUND,
                "{0} does not exist".format(str(pair))
            )

        already_added = Progression.objects.filter(
            user=user,
            pair=pair
        ).first()

        if already_added is None and pair:
            pair.learners += 1
            pair.save()

            p = Progression(
                user=user,
                pair=pair
            )
            p.save()
        else:
            logger.critical(
                "%s was already added for user %s",
                pair,
                user
            )

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
        ret_json = BaseUserSerializer(user)

        return success(ret_json.data)

    return error(RESP_BAD_REQ, "Invalid input data")
