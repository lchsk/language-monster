from serializers import (
    BaseLanguageSerializer,
    # LanguageSerializer,
    LanguagePairSerializer,
    UserProgressionSerializer,
    BaseUserSerializer,
    # MonsterUserGameSerializer,
    DataSetSerializer,
    language_pair_serializer_url,
    games_serializer_url,
    user_serializer_url,
)
from rest_framework.decorators import api_view
from models import *
from core.models import *
from core.impl.user import *
from vocabulary.impl.study import *
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

@api_view(['GET'])
def language(request, key, acronym):
    pass

    # needed_keys = ['acronym']

    # if not dict_contains_keys(request.data, needed_keys):
    #     return Response({}, status=status.HTTP_400_BAD_REQUEST)
    #
    # if request.method == 'GET':
    #     try:
    #         lang = Language.objects(acronym=acronym).first()
    #     except Exception, e:
    #         return Response({}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    #
    #     if not lang:
    #         return Response({}, status=status.HTTP_404_NOT_FOUND)
    #
    #     j = LanguageSerializer(lang)
    #
    #     return Response(j.data, status=status.HTTP_200_OK)




@api_view(['GET'])
@validate('GET /api/users/<email>/stats')
def user_stats(request, email, *args, **kwargs):
    """
        returns user's stats
    """

    if request.method == METHOD_GET:

        u = kwargs['AUTHORIZED_CONTENT']

        if not u:
            return error(RESP_UNAUTH, "Invalid token")

        if u.user.email != email:
            return error(RESP_UNAUTH, "Wrong email/token pair")

        d = Progression.objects.filter(user=u)

        for i in d:
            language_pair_serializer_url(i.pair)

        j = UserProgressionSerializer(d, many=True)

        return success(j.data)

    return error(RESP_SERV_ERR, "Unexpected error")


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
@validate('get_datasets')
def get_datasets(request, base, target, *args, **kwargs):
    """
        returns datasets available for a language pair
    """

    if request.method == METHOD_GET:
        try:
            b = Language.objects.filter(acronym=base).first()
            t = Language.objects.filter(acronym=target).first()

            if not b or not t:
                return error(
                    RESP_NOT_FOUND,
                    "{0} or {1} was not found".format(base, target)
                )

            pair = LanguagePair.objects.filter(
                base_language=b,
                target_language=t
            ).first()

            if not pair:
                return error(
                    RESP_NOT_FOUND,
                    "Pair {0} was not found".format(str(pair))
                )

            ds = DataSet.objects.filter(pair=pair, visible=True)

        except Exception, e:
            return error(RESP_SERV_ERR, str(e))

        if not ds:
            return error(RESP_NOT_FOUND, "No data sets were found")

        if CONST['USE_FULL_URLS']:
            for b in ds:
                fix_url(b.pair.base_language, 'flag_filename', 'FLAG_DIR')
                fix_url(
                    b.pair.base_language,
                    'image_filename',
                    'COUNTRIES_DIR'
                )
                fix_url(b.pair.target_language, 'flag_filename', 'FLAG_DIR')
                fix_url(
                    b.pair.target_language,
                    'image_filename',
                    'COUNTRIES_DIR'
                )

        j = DataSetSerializer(ds, many=True)

        return success(j.data)


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


from django.http import Http404
# from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from api.views2.base import *

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


@api_view(['GET'])
@validate('get_words')
def get_words(request, dataset_id, email, *args, **kwargs):
    '''
        returns words from a dataset prepared for a specific user

        /data/<dataset_id>/<email>
    '''

    if request.method == METHOD_GET:

        u = kwargs['AUTHORIZED_CONTENT']

        if not u:
            return error(RESP_UNAUTH, "Invalid token")

        if u.user.email != email:
            return error(RESP_UNAUTH, "Wrong email/token pair")

        d = DataSet.objects.filter(id=dataset_id).first()
        # TODO: add API call to add new language to learn

        p = Progression(
            user=u,
            pair=d.pair
        )
        p.save()

        words = game_data(d, u, 10, to_json=False)

        if words:
            return success(words)
        else:
            return error(RESP_NOT_FOUND, "Words not found")

        # return get_game_data(request, dataset_id, u.email)

    return error(RESP_BAD_REQ)
