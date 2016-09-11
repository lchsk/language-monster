from serializers import (
    BaseLanguageSerializer,
    # LanguageSerializer,
    LanguagePairSerializer,
    UserProgressionSerializer,
    BaseUserSerializer,
    # MonsterUserGameSerializer,
    DataSetSerializer,
    GetWordsFilters,
    # GetWordsResponse,
    GetWordsSingleSetSerializer,
    language_pair_serializer_url,
    games_serializer_url,
    user_serializer_url,
)
from rest_framework.decorators import api_view
from models import *
from core.models import *
from core.impl.user import *
from vocabulary.impl.study import *
from vocabulary.impl.study import get_game_words
from django.conf import settings

from core.impl import mail
from django.core.urlresolvers import reverse
from utility.interface import *

from api.helper.api_call import *
from utility.api_utils import (
    validate,
    CONST,
    fix_url,
)

logger = logging.getLogger(__name__)
settings.LOGGER(logger, settings.LOG_API_HANDLER)

from core.data.base_language import BASE_LANGUAGES
from core.data.language_pair import LANGUAGE_PAIRS_FLAT

from django.http import Http404
# from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from api.views2.base import *

class UserStats(MonsterUserAuthView):
    def get(self, request):
        progression = Progression.objects.filter(user=self.monster_user)

        resp = UserProgressionSerializer(progression, many=True)

        return self.success(resp.data)


@api_view(['GET'])
@validate('games')
def games(request, *args, **kwargs):
    """
        list of available games
    """

    if request.method == METHOD_GET:
        try:
            d = settings.GAMES
        except Exception, e:
            return error(RESP_SERV_ERR, str(e))

        if not d:
            return error(RESP_NOT_FOUND, "Games not found")

        for k, v in d.iteritems():
            games_serializer_url(v)

        return success(d)

    return error(RESP_METHOD_NOT_ALLOWED, "Not allowed")





@api_view(['GET'])
@validate('GET /api/users/<email>/password')
def password(request, email, *args, **kwargs):
    """
        get new password
    """

    print email

    if request.method == METHOD_GET:

        device = kwargs['AUTHORIZED_CONTENT']

        if not device:
            return error(RESP_UNAUTH, "Invalid token")

        u = MonsterUser.objects.filter(user__email=email).first()

        if not u:
            return error(RESP_NOT_FOUND, "Email not found")

        secure_hash = create_hash(u)
        u.secure_hash = secure_hash
        u.save()

        try:
            host = request.get_host()
            url = reverse('core:generate_password', args=[secure_hash])

            mail.send_template_email(
                request=request,
                recipient=u.user.email,
                template='password_recovery',
                ctx={
                    'PUBLIC_NAME': u.public_name,
                    'URL': 'http://' + host + url
                }
            )
        except Exception:
            return error(RESP_SERV_ERR, "Could not send password email")

        return success({})

    return error(RESP_SERV_ERR, "Unexpected error")



class Languages(APIAuthView):
    def get(self, request):
        resp = BaseLanguageSerializer(
            BASE_LANGUAGES.values(),
            many=True
        )

        return self.success(resp.data)

class Ping(APIAuthView):
    def get(self, request):
        return self.success({})

class LanguagesToLearn(APIAuthView):
    def get(self, request):
        resp = LanguagePairSerializer(
            LANGUAGE_PAIRS_FLAT.values(),
            many=True
        )

        return self.success(resp.data)

class AvailableDatasets(APIAuthView):
    def get(self, request, lang_pair):
        datasets = DataSet.objects.filter(
            lang_pair=lang_pair,
            visible=True,
            status='A',
        )

        resp = DataSetSerializer(datasets, many=True)

        return success(resp.data)

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

        return success(resp.data)

@api_view(['GET'])
@validate('languages')
def languages(request, *args, **kwargs):
    """
        /languages
    """

    if request.method == METHOD_GET:
        try:
            bl = BaseLanguage.objects.all()
        except Exception:
            # TODO: return actual error
            return error()

        if not bl:
            return error(RESP_NOT_FOUND, "Languages not found")

        if CONST['USE_FULL_URLS']:
            for b in bl:
                fix_url(b, 'flag_filename', 'FLAG_DIR')
                fix_url(b.language, 'flag_filename', 'FLAG_DIR')
                fix_url(b.language, 'image_filename', 'COUNTRIES_DIR')

        serialized = BaseLanguageSerializer(bl, many=True)
        return success(serialized.data)

    return error()


@api_view(['GET'])
@validate('GET /api/users/<email>')
def get_user(request, email, *args, **kwargs):

    u = kwargs['AUTHORIZED_CONTENT']

    if not u:
        logger.warning("Invalid token")
        return error(RESP_UNAUTH, "Invalid token")

    if u.user.email != email:
        logger.warning("Wrong email/token pair")
        return error(RESP_UNAUTH, "Wrong email/token pair")

    try:
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
        serialized = BaseUserSerializer(u)

        user_serializer_url(u)

        return success(serialized.data)
    except Exception as e:
        logger.critical("Error when returning a user: %s", str(e))
        return error(RESP_BAD_REQ, str(e))
