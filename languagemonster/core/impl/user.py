import re
import os
import copy
import logging
import random
import uuid

from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.auth import models as contrib_models

from core.models import MonsterUser

from utility.security import get_secure_hash

logger = logging.getLogger(__name__)

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
            muser.api_login_hash = get_secure_hash()
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
        error_str = _('msg_passwords_not_equal')

    # length of the password must be >= 8
    if len(p_user['password1']) < 8:
        error = 'password_too_short'
        error_str = _('msg_password_too_short')

    if not re.match(r"[^@]+@[^@]+\.[^@]+", p_user['email']):
        error = 'email_invalid'
        error_str = _('msg_invalid_email')

    # check if email address is unique
    email = contrib_models.User.objects.filter(email=p_user['email'])
    if len(email) > 0:
        error = 'email_not_unique'
        error_str = _('msg_email_already_in_use')

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
        monster_user.public_name = monster_user.user.email


def process_games_list(games, user_games):
    """Mark games not selected by the user."""

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


def register(
    email,
    password1,
    password2,
    confirmation_required,
    base_language,
):
    user = {
        'password1': password1,
        'password2': password2,
        'email': email,
    }

    valid, error, error_str = is_registration_valid(user)

    if valid:
        logger.info("User registration for %s data is valid", email)

        u = contrib_models.User.objects.create_user(
            email=email,
            password=password1,
            username=email
        )
        mu = MonsterUser(user=u)
        u.is_active = not confirmation_required

        secure_hash = uuid.uuid4().hex
        mu.secure_hash = secure_hash

        api_login_hash = uuid.uuid4().hex
        mu.api_login_hash = api_login_hash

        mu.country = base_language.country.upper()
        mu.language = base_language.symbol

        mu.avatar = get_default_avatar(mu.country)
        mu.uri = uuid.uuid4().hex

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
