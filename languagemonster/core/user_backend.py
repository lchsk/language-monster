import re
import os
import copy
import logging
import random

from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.auth import models as contrib_models

from core.models import MonsterUser
from utility.interface import (
    create_hash,
    get_uuid_str,
)

logger = logging.getLogger(__name__)
settings.LOGGER(logger, settings.LOG_WWW_HANDLER)

def authenticate_user(
    username=None,
    email=None,
    password=None,
    new_hash=False
):
    if not username and email:
        muser = MonsterUser.objects.filter(
            user__email=email
        ).select_related('user').first()

        if not muser:
            logger.warning(
                'User %s not found',
                muser
            )
            return False

        username = muser.user.username
    else:
        return False

    if muser.user.check_password(password):
        if new_hash:
            muser.api_login_hash = create_hash(muser)
            muser.save()

        logger.warning(
            'User %s authorised',
            muser
        )
        return muser
    else:
        logger.warning(
            'User %s not authorised',
            muser
        )
        return False


def is_registration_valid(p_user):
    '''
        p_user must be:
        {
            'password1': 'password1,
            'password2': 'password2,
            'email': 'email'
        }
    '''
    error = None
    error_str = ''

    # password must be of the same length
    if p_user['password1'] != p_user['password2']:
        error = 'passwords_not_equal'
        error_str = _('Passwords are not equal.')

    # length of the password must be >= 8
    if len(p_user['password1']) < 8:
        error = 'password_too_short'
        error_str = _('Password must be at least 8 characters long.')

    # TODO: Add email validation
    # email address validation
    # try:
    #     EmailField().clean(p_user['email'])
    # except ValidationError:
    #     error = 'email_invalid'
    #     error_str = 'That email address is not valid.'

    # more strict: "^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$"
    if not re.match(r"[^@]+@[^@]+\.[^@]+", p_user['email']):
        error = 'email_invalid'
        error_str = _('That email address is not valid.')

    # check if email address is unique
    email = contrib_models.User.objects.filter(email=p_user['email'])
    if len(email) > 0:
        error = 'email_not_unique'
        error_str = _(
            'That email was already used on this website. Pick a new one.'
        )

    if error is None:
        return (True, '', '')
    else:
        return (False, error, error_str)


def update_public_name(monster_user):
    if monster_user.user.first_name and monster_user.user.last_name:
        monster_user.public_name = (
            u'{0} {1}'.format(
                monster_user.user.first_name,
                monster_user.user.last_name
            )
        )
    elif monster_user.user.first_name:
        monster_user.public_name = monster_user.user.first_name
    else:
        monster_user.user.public_name = monster_user.user.email


def process_games_list(monster_user, games, user_games):
    ''' Mark games not selected by the user'''

    banned_games = [
        user_game['game']
        for user_game in user_games
        if user_game['banned']
    ]

    res = copy.deepcopy(games)

    for game in banned_games:
        if game in res:
            res[game]['available'] = False

    return res


def get_default_avatar(country):
    if (
        country and
        os.path.exists(
            settings.AVATARS_URL_FULL + country.lower() + '.jpg'
        )
    ):
        return country.lower() + '.jpg'
    else:
        return random.choice([
            'lion.jpg', 'tiger.jpg', 'koala.jpg', 'elephant.jpg', 'grizzly.jpg'
        ])


def register(email, password1, password2, confirm, base_language):
    user = {
        'password1': password1,
        'password2': password2,
        'email': email
    }

    valid, error, error_str = is_registration_valid(user)

    if valid:
        logger.info(
            "User registration data is valid"
        )

        u = contrib_models.User.objects.create_user(
            email=email,
            password=password1,
            username=email
        )
        mu = MonsterUser(user=u)
        u.is_active = not confirm

        secure_hash = create_hash(mu)
        mu.secure_hash = secure_hash

        api_login_hash = create_hash(mu)
        mu.api_login_hash = api_login_hash

        if email in settings.SUPERADMIN_EMAIL:
            u.is_staff = True
            u.is_superuser = True

        mu.country = base_language.country.upper()
        mu.language = base_language.symbol

        mu.avatar = get_default_avatar(mu.country)
        mu.uri = get_uuid_str()

        update_public_name(mu)
        u.save()
        mu.save()

        return True, '', ''

    else:
        logger.info(
            "User registration data is invalid: %s",
            error_str
        )

        return False, error, error_str

from social.apps.django_app.middleware import SocialAuthExceptionMiddleware
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse


class SocialAuthExceptionMiddleware(SocialAuthExceptionMiddleware):
    def process_exception(self, request, exception):
        print str(type(exception))
        return HttpResponseRedirect(reverse('info', args=['social_auth_exception']))
        # if type(exception) == AuthCanceled:
        #     return render(request, "pysocial/authcancelled.html", {})
        # else:
        #     pass


def set_user_params(backend, user, response, *args, **kwargs):
    '''Python social auth'''

    # http://graph.facebook.com/764823056966540/picture

    if backend.name == 'facebook':
        if response and 'id' in response and 'email' in response:
            u = MonsterUser.objects(email=response.get('email'))
            locale = response.get('locale', 'en_GB')

            if len(u) == 1:
                u = u[0]
                u.social_account = True
                if not u.uri:
                    u.uri = str(u.id)
                u.save()

                if not u.base_language or not u.current_language:
                    # De facto: new user
                    # Set base/current language
                    base_language = None

                    base = find_base_language(locale)

                    base_language = base if base else landing_language(request)

                    if base_language:
                        u.base_language = base_language
                        u.current_language = base_language.language
                        u.save()

                if not u.country and len(locale) >= 2:
                    u.country = locale[-2:].upper()
                    u.save()

                if not u.gender and 'gender' in response:

                    if response['gender'] == 'male':
                        u.gender = 'M'
                    elif response['gender'] == 'female':
                        u.gender = 'F'

                    u.save()

                # avatar
                if not u.avatar and len(locale) >= 2:

                    url = 'http://graph.facebook.com/{0}/picture'.format(response['id'])
                    from requests import request

                    try:
                        resp = request('GET', url, params={'type': 'large'})
                        resp.raise_for_status()
                    except Exception:
                        u.avatar = get_default_avatar(locale[-2:])
                    else:
                        filename = str(response.get('id'))
                        path = settings.PROJECT_ROOT + settings.STATIC_URL + settings.AVATARS_URL + filename
                        path = os.path.normpath(path)

                        with open(path, 'wb+') as destination:
                            destination.write(resp.content)

                        u.avatar = filename

                    u.save()

                if not u.public_name:
                    u.public_name = response.get('name', 'email')
                    u.save()
