from django.conf import settings

from core.models import *
from core.models import (
    MobileDevice,
    MonsterUser,
)

from api.helper.calls import CALLS
from api.helper.api_call import (
    AUTH_NO_AUTH,
    AUTH_API_KEY,
    AUTH_DEVICE_KEY,
    AUTH_USER_KEY,
    error,
    RESP_BAD_REQ,
    RESP_UNAUTH,
)


CONST = dict(
    # If true, full urls will be returned for files

    USE_FULL_URLS=True,
    FLAG_DIR="{monster}/static/images/flags/".format(
        monster=settings.MONSTER_URL
    ),
    COUNTRIES_DIR="{monster}/static/images/countries/".format(
        monster=settings.MONSTER_URL
    ),
    AVATARS_DIR="{monster}/static/images/avatars/".format(
        monster=settings.MONSTER_URL
    ),
    GAMES_IMAGES_DIR="{monster}/static/images/marketing/games/".format(
        monster=settings.MONSTER_URL
    ),
)


def fix_url(obj, field, const):
    if isinstance(obj, dict):
        if '/' in obj[field]:
            return
        obj[field] = CONST[const] + obj[field]
    elif isinstance(obj, object):
        if '/' in str(getattr(obj, field)):
            return
        setattr(obj, field, CONST[const] + str(getattr(obj, field)))


def _check_auth(c, r):
    """
        checks if call contains proper authorization

        returns (
            <bool> - true if authorized
            <reason> - explanation if above is false
            <object> - additional authorized object (eg. user)
        )
    """

    auth = r.META.get('HTTP_AUTHORIZATION', None)

    if not auth:
        return False, "No authorization token", None

    try:
        _, token = auth.split(' ')
    except Exception:
        return False, "Invalid authorization format", None

    if c.auth == AUTH_API_KEY:
        if token == settings.API_KEY:
            return True, '', None
    elif c.auth == AUTH_DEVICE_KEY:

        d = MobileDevice.objects.filter(
            device_key=token
        ).first()

        if d:
            return True, '', d

    elif c.auth == AUTH_USER_KEY:

        u = MonsterUser.objects.filter(
            api_login_hash=token
        ).first()

        if u:
            return True, '', u

    return False, 'Authorization invalid', None


def _check_content(c, r):
    """
        checks if request contains mandatory fields
    """

    if not isinstance(r.data, dict):
        return False, 'Incorrect format of JSON'

    for f in c.fields:
        if f.required and f.name not in r.data:
            return False, 'Required field <{0}> is missing'.format(f.name)

    if not c.additional_fields:

        fields = [f.name for f in c.fields]

        for k, _ in r.data.iteritems():
            if k not in fields:
                return False, '<{0}> was not expected'.format(k)

    return True, ''


def validate(path=None):
    """
        validates an API call
    """

    def decorator(f):

        def call(*args, **kwargs):

            if path:
                identifier = path
            else:
                identifier = f.__name__

            if len(args) < 1:
                return error(RESP_BAD_REQ, 'No request received')

            if identifier not in CALLS:
                return error(
                    RESP_BAD_REQ, 'Identifier <{0}> does not exist'.format(
                        identifier
                    )
                )

            c = CALLS[identifier]
            r = args[0]

            valid, reason, obj = _check_auth(c, r)

            if valid:

                content, expl = _check_content(c, r)

                if content:
                    kwargs['AUTHORIZED_CONTENT'] = obj
                    return f(*args, **kwargs)
                else:
                    return error(RESP_BAD_REQ, expl)

            else:
                return error(RESP_UNAUTH, reason)

        return call
    return decorator
