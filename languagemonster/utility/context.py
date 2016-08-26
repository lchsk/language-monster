from collections import namedtuple
from uuid import uuid4
import os

from django.conf import settings
from django.contrib import messages
from django.utils import translation

from utility.url import get_urls
from utility.user_language import landing_language
from core.impl.user import update_public_name

from core.data.base_language import BASE_LANGUAGES
from core.data.language_pair import LANGUAGE_PAIRS_FLAT
from core.data.language import LANGUAGES

from core.models import (
    MonsterUser,
    BaseLanguage,
    Progression,
    MonsterUserGame,
)

Status = namedtuple('Status', [
    'debug',
    'version',
    'branch',
])

class MonsterUserAuth(object):
    def __init__(self, monster_user):
        self._monster_user = monster_user
        self._language = BASE_LANGUAGES[self._monster_user.language]

        studying = [
            (p, LANGUAGE_PAIRS_FLAT.get(p.lang_pair))
            for p in Progression.objects.filter(
                user=self._monster_user
            )
        ]

        self._studying = filter(
            lambda x: \
            x[1].base_language.acronym == self._language.language.acronym,
            studying
        )

    def update(self,
        first_name,
        last_name,
        gender,
        country,
        www,
        location,
        about,
        uri,
    ):
        self._monster_user.user.first_name = first_name
        self._monster_user.user.last_name = last_name
        self._monster_user.gender = gender
        self._monster_user.country = country
        self._monster_user.www = www
        self._monster_user.location = location
        self._monster_user.about = about
        # self._monster_user.uri = uri.replace(' ', '')

        update_public_name(self._monster_user)
        self._monster_user.user.save()
        self._monster_user.save()

    def change_password(self, password):
        self._monster_user.user.set_password(password)
        self._monster_user.user.save()

    def change_language(self, language):
        self._monster_user.language = language
        self._monster_user.save()

    def change_email(self, email):
        secure_hash = uuid4().hex

        self._monster_user.new_email = email
        self._monster_user.secure_hash = secure_hash
        self._monster_user.save()

        return secure_hash

    def save_new_email(self):
        self._monster_user.user.email = self._monster_user.new_email
        self._monster_user.user.save()

        self._monster_user.secure_hash = None
        self._monster_user.new_email = None
        update_public_name(self._monster_user)

        self._monster_user.save()

    def update_games(self, res):
        for game, game_settings in res.iteritems():
            user_game = MonsterUserGame.objects.filter(
                monster_user=self._monster_user,
                game=game
            ).first()

            if not user_game:
                user_game = MonsterUserGame(
                    monster_user=self._monster_user,
                    game=game,
                )

            user_game.banned = not game_settings['available']
            user_game.save()

    def save_avatar(self, obj, content_type):
        if content_type == 'jpeg':
            content_type = 'jpg'

        new_name = uuid4().hex + '.' + content_type

        path = settings.AVATARS_URL_FULL + new_name
        path = os.path.normpath(path)

        with open(path, 'wb+') as destination:
            for chunk in obj.chunks():
                destination.write(chunk)

        self._monster_user.avatar = new_name
        self._monster_user.save()

    @property
    def email(self):
        return self._monster_user.user.email

    @property
    def about(self):
        return self._monster_user.about

    @property
    def www(self):
        return self._monster_user.www

    @property
    def country(self):
        return self._monster_user.country

    @property
    def location(self):
        return self._monster_user.location

    @property
    def gender(self):
        return self._monster_user.gender

    @property
    def first_name(self):
        return self._monster_user.user.first_name

    @property
    def last_name(self):
        return self._monster_user.user.last_name

    @property
    def raw(self):
        return self._monster_user

    @property
    def uri(self):
        return self._monster_user.uri

    @property
    def id(self):
        return self._monster_user.id

    @property
    def public_name(self):
        return self._monster_user.public_name

    @property
    def avatar(self):
        return self._monster_user.avatar

    @property
    def studying(self):
        return self._studying

    @property
    def language(self):
        return self._language

    @property
    def secure_hash(self):
        return self._monster_user.secure_hash

class Context(object):
    def __init__(self, request):
        self._request = request
        self._status = None
        self._base_languages = []
        self._urls = []
        self._messages = []
        self._is_authorised = False
        self._monster_user = None
        self._landing_language = None

        self._build_common()

    @property
    def urls(self):
        return self._urls

    @property
    def base_languages(self):
        return self._base_languages

    @property
    def language(self):
        if self._is_authorised:
            return self._monster_user.language
        else:
            return self._landing_language

    @property
    def user(self):
        return self._monster_user

    @property
    def is_authorised(self):
        return self._is_authorised

    def _load_user(self, pk):
        return MonsterUser.objects.filter(
            user__id=pk
        ).select_related('user').first()

    def _get_user(self):
        pk = self._request.session.get('_auth_user_id')

        if pk is None:
            self._is_authorised = False
        else:
            monster_user = self._load_user(pk)

            if monster_user is None:
                self._is_authorised = False
            else:
                self._is_authorised = monster_user.user.is_authenticated()

        if self._is_authorised:
            self._monster_user = MonsterUserAuth(monster_user)
            translation.activate(self._monster_user.language.language.acronym)
        else:
            self._landing_language = landing_language(self._request)
            translation.activate(self._landing_language.language.acronym)

    def _build_common(self):
        self._status = Status(
            debug=settings.DEBUG,
            version=settings.VERSION,
            branch=settings.BRANCH,
        )

        self._base_languages = BASE_LANGUAGES
        self._urls = get_urls(self._request)
        self._messages = messages.get_messages(self._request)

        self._get_user()
