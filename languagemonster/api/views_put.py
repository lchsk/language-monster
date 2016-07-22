from utility.api_utils import (
    validate,
)
import logging
from rest_framework.decorators import api_view
from serializers import *
from django.conf import settings

import core.views as views
from api.helper.api_call import *
from utility.interface import create_hash
import core.mail as mail
from django.core.urlresolvers import reverse
from core.user_backend import update_public_name

logger = logging.getLogger(__name__)
settings.LOGGER(logger, settings.LOG_API_HANDLER)


@api_view(['PUT'])
@validate('PUT /api/users/email')
def change_user_email(request, *args, **kwargs):
    """
        change user's email

        PUT /users/email
    """

    if request.method == METHOD_PUT:

        u = kwargs.get('AUTHORIZED_CONTENT', None)

        if not u:
            return error(RESP_NOT_FOUND, "Invalid authorization")

        new_email = request.data['email']

        if not new_email:
            return error(
                RESP_NOT_FOUND,
                "{email} does not exist".format(email=new_email)
            )

        u.new_email = new_email

        secure_hash = create_hash(u)
        u.secure_hash = secure_hash
        u.save()

        try:
            host = request.get_host()
            url = reverse('core:confirm_email', args=[secure_hash])

            mail.send_template_email(
                request=request,
                recipient=new_email,
                template='email_change',
                ctx={
                    'PUBLIC_NAME': u.public_name,
                    'URL': 'http://' + host + url
                }
            )

        except Exception, e:
            logging.critical("Failed to send confirmation email: %s", e)
            return error(RESP_SERV_ERR, "Could not send confirmation email")

        return success({})

    return error(RESP_BAD_REQ, "Invalid request")


@api_view(['PUT'])
@validate('PUT /api/users/language')
def set_language(request, *args, **kwargs):
    """
        set user's current/base language

        PUT /users/language
    """

    if request.method == METHOD_PUT:

        u = kwargs.get('AUTHORIZED_CONTENT', None)

        if not u:
            return error(RESP_NOT_FOUND, "Invalid authorization")

        country = request.data['country'].lower()

        b = BaseLanguage.objects.filter(
            country=country
        ).first()

        if b:
            u.base_language = b
            u.current_language = b.language
            u.save()
        else:
            return error(
                RESP_BAD_REQ,
                "Country {country} was not found".format(country=country)
            )

        user_serializer_url(u)

        # TODO: find better way to fill MonsterUser with banned/played games
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
        ret_json = BaseUserSerializer(u)

        return success(ret_json.data)

    return error(RESP_BAD_REQ, "Invalid request")


@api_view(['PUT'])
@validate('set_banned_games')
def set_banned_games(request, *args, **kwargs):
    """
        set games the user does not want to play

        PUT /users/games
    """

    if request.method == METHOD_PUT:

        u = kwargs.get('AUTHORIZED_CONTENT', None)

        if not u:
            return error(RESP_NOT_FOUND, "Invalid authorization")

        # user_games = MonsterUserGame.objects.filter(
        #     monster_user=c['user'],
        #     # game=game
        # )

        games = settings.GAMES
        res = {}
        banned = request.data['banned']

        for k, v in games.iteritems():
            res[k] = {}
            res[k]['available'] = True

            if k in banned:
                res[k]['available'] = False

        views.update_games(res, u)
        # u.banned_games = request.data['banned']
        # u.save()

        user_serializer_url(u)

        # TODO: find better way to fill MonsterUser with banned/played games
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
        ret_json = BaseUserSerializer(u)

        return success(ret_json.data)

    return error(RESP_BAD_REQ, "Invalid request")


@validate('PUT /api/users/<email>')
def update_user(request, email, *args, **kwargs):

    serializer = UserDetailsUpdateRequest(data=request.data)

    if serializer.is_valid():

        u = kwargs['AUTHORIZED_CONTENT']

        if not u:
            return error(RESP_UNAUTH, "Invalid token")

        if u.user.email != email:
            return error(RESP_UNAUTH, "Wrong email/token pair")

        try:
            # populate_from_dict(request.data, MonsterUser, u)

            if serializer['first_name'].value:
                u.user.first_name = serializer['first_name'].value

            if serializer['last_name'].value:
                u.user.last_name = serializer['last_name'].value

            if serializer['country'].value:
                u.country = serializer['country'].value
            if serializer['gender'].value:
                u.gender = serializer['gender'].value
            if serializer['location'].value:
                u.location = serializer['location'].value

            if serializer['uri'].value:
                u.uri = serializer['uri'].value

            if serializer['www'].value:
                u.www = serializer['www'].value

            if serializer['birthday'].value:
                u.birthday = serializer['birthday'].value

            if serializer['about'].value:
                u.about = serializer['about'].value

            update_public_name(u)
            u.save()

            user_serializer_url(u)

            # TODO:
            # find better way to fill MonsterUser with banned/played games
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
            ret_json = BaseUserSerializer(u)

            return success(ret_json.data)
        except Exception, e:
            return error(RESP_BAD_REQ, str(e))
    else:
        logger.critical(serializer.errors)
        return error(RESP_BAD_REQ, serializer.errors)
