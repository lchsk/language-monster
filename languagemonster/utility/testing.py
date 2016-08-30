import os
import os.path
import httplib
import json
import uuid
import random
import inspect

from django.conf import settings
from core.models import (
    DataSet,
    MonsterUser,
    BaseLanguage,
    MobileDevice,
    Progression,
    UserResult,
    UserWordPair,
)
from django.contrib.auth import models as contrib_models

from api.helper.calls import *

def assert_subclasses(classes, class_, predicate):
    """Ensure that all classes are of required class_.

        classes([(string name, class)]): A list of tuples (name, class)

        class_(class): Required class

        predicate(function): Function to select items from classes based
            on the name. Must return either True of False.
    """

    for name, cbv in classes:
        if inspect.isclass(cbv) and predicate(name):
            assert issubclass(cbv, class_)


###########

MONSTER_EMAIL = 'monster@language-monster.com'
TEST_EMAIL = MONSTER_EMAIL
TEST_USER_PASSWORD = '12345678'

TEST_OS = '__TEST_OS__'
TEST_DEVICE_KEY = 'd4b0a62e353c463a97e617f4e74d4bbb'


def get_random_dataset():
    datasets = DataSet.objects.all()

    return random.choice(datasets)


def get_test_user():
    test_user = MonsterUser.objects.filter(
        user__email=TEST_EMAIL
    ).first()

    if not test_user:
        u = contrib_models.User.objects.create_user(
            email=TEST_EMAIL,
            password=TEST_USER_PASSWORD,
            username='test',
            first_name='Bugs',
            last_name='Bunny'
        )

        base_languages = BaseLanguage.objects.all()
        random_base_language = random.choice(base_languages)

        mu = MonsterUser(
            api_login_hash=uuid.uuid4().hex,
            current_language=random_base_language.language,
            base_language=random_base_language
        )
        mu.user = u
        u.save()
        mu.save()
        test_user = mu

    return test_user


def get_test_device():
    test_device = MobileDevice.objects.filter(
        os=TEST_OS,
        device_key=TEST_DEVICE_KEY
    ).first()

    if not test_device:
        test_device = MobileDevice(
            os=TEST_OS,
            device_key=TEST_DEVICE_KEY
        )
        test_device.save()

    return test_device


def remove_test_user():
    users = MonsterUser.objects.filter(
        user__email=TEST_EMAIL
    )

    for u in users:
        u.user.delete()
        u.delete()


def _remove_test_device():
    devices = MobileDevice.objects.filter(
        os=TEST_OS
    )

    for d in devices:
        d.delete()


def remove_test_data(**kwargs):
    """
        removes data needed only for testing
    """

    user = kwargs.get('user')
    device = kwargs.get('device')

    if device:
        _remove_test_device()

    if user:
        progs = Progression.objects.filter(user=user)

        for p in progs:
            p.delete()

        word_pairs = UserWordPair.objects.filter(user=user)

        for wp in word_pairs:
            wp.delete()

        user_results = UserResult.objects.filter(user=user)

        for ur in user_results:
            ur.delete()

        remove_test_user()


def api_host():
    """
        returns API host
        by default: localhost:8000
    """

    return os.getenv('MONSTER_HOST', 'localhost:8000')


def verbose():
    """
        returns true if there's an environment variable set
        to show everything that's going on with the tests
    """

    return os.getenv('VERBOSE_TEST', 'false') == 'true'


def http_conn():
    """
        returns HTTP connection
    """

    return httplib.HTTPConnection(api_host())


def json_headers():
    """
        returns HTTP headers for JSON-based API
    """

    return {
        "Content-type": "application/json",
        "Accept": "application/json",
        "Charset": "utf-8",
    }


def headers(call, **kwargs):
    """
        returns headers based on the authorization method
    """

    # Get json headers

    json = json_headers()

    auth = call.auth

    if auth == AUTH_API_KEY:
        json['Authorization'] = '{0} {1}'.format('Token', settings.API_KEY)

    elif auth == AUTH_DEVICE_KEY:
        json['Authorization'] = '{0} {1}'.format(
            'Token',
            kwargs['device'].device_key
        )

    elif auth == AUTH_USER_KEY:
        json['Authorization'] = '{0} {1}'.format(
            'Token',
            kwargs['user'].api_login_hash
        )

    elif auth == AUTH_NO_AUTH:
        # No auth in this call
        pass

    else:
        raise Exception('Invalid authorization method')

    return json


def req(conn, identifier, body, **kwargs):
    """
        make a request
    """

    if identifier in CALLS:
        call = CALLS[identifier]

        url = call.url

        if 'args' in kwargs:
            args = kwargs['args']
            url = url.format(*args)

        if verbose():
            print
            print '>' * 80
            print call.method, url
            print json.dumps(
                body,
                indent=4,
                sort_keys=True
            )
            print '=' * 80
            print

        conn.request(
            call.method,
            url,
            json.dumps(body),
            headers(call, **kwargs)
        )


def resp(conn):
    """
        prepares an HTTP response for the user
    """

    tmp = conn.getresponse()

    body = tmp.read()

    if verbose():
        try:
            print '<' * 80
            print tmp.status, tmp.reason

            print json.dumps(
                json.loads(body),
                indent=4,
                sort_keys=True
            )

            print '=' * 80
            print
        except ValueError:
            print body

    try:
        body = json.loads(body)
    except Exception as e:
        print str(e)
        print body

    ret = {
        'raw': tmp,
        'status': tmp.status,
        'data': body
    }

    return ret


def get_random_unicode(length=random.randint(1, 12)):

    try:
        get_char = unichr
    except NameError:
        get_char = chr

    include_ranges = [
        (0x0021, 0x0021),
        (0x0023, 0x0026),
        (0x0028, 0x007E),
        (0x00A1, 0x00AC),
        (0x00AE, 0x00FF),
        (0x0100, 0x017F),
        (0x0180, 0x024F),
        (0x2C60, 0x2C7F),
        (0x16A0, 0x16F0),
        (0x0370, 0x0377),
        (0x037A, 0x037E),
        (0x0384, 0x038A),
        (0x038C, 0x038C),
    ]

    alphabet = [
        get_char(code_point)
        for current_range in include_ranges
        for code_point in range(current_range[0], current_range[1] + 1)
    ]
    return u''.join(
        random.choice(alphabet)
        for i in range(length)
    )
