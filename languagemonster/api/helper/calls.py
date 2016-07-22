from api.helper.api_call import *

TEST_EMAIL = 'monster@language-monster.com'
CALLS = {}

def register(call):
    """
        registers an API call

        @call instance of ApiCall
    """

    CALLS[call.identifier] = call

register(
    ApiCall(
        identifier = 'devices',
        url = '/api/devices',
        method = METHOD_POST,
        auth = AUTH_API_KEY,
        fields = [
            ApiField('os', dtype=TYPE_STR, required=False),
            ApiField('ip', dtype=TYPE_STR, required=False),
            ApiField('device', dtype=TYPE_STR, required=False),
            ApiField('display', dtype=TYPE_STR, required=False),
            ApiField('hardware', dtype=TYPE_STR, required=False),
            ApiField('manufacturer', dtype=TYPE_STR, required=False),
            ApiField('model', dtype=TYPE_STR, required=False),
            ApiField('sdk', dtype=TYPE_STR, required=False),
            ApiField('language', dtype=TYPE_STR, required=False),
        ],
        additional_fields = True
    )
)

register(
    ApiCall(
        identifier = 'languages',
        url = '/api/languages',
        method = METHOD_GET,
        auth = AUTH_DEVICE_KEY,
        fields = [],
        additional_fields = False
    )
)

register(
    ApiCall(
        identifier = 'language_pairs',
        url = '/api/languages/pairs',
        method = METHOD_GET,
        auth = AUTH_DEVICE_KEY,
        fields = [],
        additional_fields = False
    )
)

register(
    ApiCall(
        identifier = 'games',
        url = '/api/games',
        method = METHOD_GET,
        auth = AUTH_DEVICE_KEY,
        fields = [],
        additional_fields = False
    )
)

register(
    ApiCall(
        identifier = 'get_datasets',
        url = '/api/data/pl/en',
        method = METHOD_GET,
        auth = AUTH_DEVICE_KEY,
        fields = [],
        additional_fields = False
    )
)

register(
    ApiCall(
        identifier = 'get_words',
        url = '/api/data/{0}/{1}',
        method = METHOD_GET,
        auth = AUTH_USER_KEY,
        fields = [],
        additional_fields = False
    )
)

register(
    ApiCall(
        identifier = 'set_banned_games',
        url = '/api/users/games',
        method = METHOD_PUT,
        auth = AUTH_USER_KEY,
        fields = [
            # TODO: Add TYPE_LIST
            ApiField('banned', dtype=TYPE_STR, required=True),
        ],
        additional_fields = False
    )
)

# registration

register(
    ApiCall(
        identifier = 'POST /api/users',
        url = '/api/users',
        method = METHOD_POST,
        auth = AUTH_DEVICE_KEY,
        fields = [
            ApiField('email', dtype=TYPE_STR, required=True),
            ApiField('password1', dtype=TYPE_STR, required=True),
            ApiField('password2', dtype=TYPE_STR, required=True),
            ApiField('language', dtype=TYPE_STR, required=True),
            ApiField('country', dtype=TYPE_STR, required=True)
        ],
        additional_fields = False
    )
)

# login

register(
    ApiCall(
        identifier = 'PUT /api/users',
        url = '/api/users',
        method = METHOD_PUT,
        auth = AUTH_DEVICE_KEY,
        fields = [
            ApiField('email', dtype=TYPE_STR, required=True),
            ApiField('password', dtype=TYPE_STR, required=True),
        ],
        additional_fields = False
    )
)

# users starts learning new language

register(
    ApiCall(
        identifier = 'POST /api/users/begin',
        url = '/api/users/begin',
        method = METHOD_POST,
        auth = AUTH_USER_KEY,
        fields = [
            ApiField('base', dtype=TYPE_STR, required=True),
            ApiField('target', dtype=TYPE_STR, required=True),
        ],
        additional_fields = False
    )
)

# save results

register(
    ApiCall(
        identifier = 'POST /api/users/results',
        url = '/api/users/results',
        method = METHOD_POST,
        auth = AUTH_USER_KEY,
        fields = [
            ApiField('dataset_id', dtype=TYPE_STR, required=True),
            ApiField('email', dtype=TYPE_STR, required=True),
            ApiField('mark', dtype=TYPE_INT, required=True),

            # TODO: TYPE_LIST
            ApiField('words_learned', dtype=TYPE_STR, required=True),
            ApiField('to_repeat', dtype=TYPE_STR, required=True),

            ApiField('game', dtype=TYPE_STR, required=True)

        ],
        additional_fields = False
    )
)

register(
    ApiCall(
        identifier = 'POST /api/users/results/js',
        url = '/api/users/results/js',
        method = METHOD_POST,
        auth = AUTH_NO_AUTH,
        fields = [
            ApiField('game_session_id', dtype=TYPE_STR, required=True),

            ApiField('dataset_id', dtype=TYPE_STR, required=True),
            ApiField('email', dtype=TYPE_STR, required=True),
            ApiField('mark', dtype=TYPE_INT, required=True),

            # TODO: TYPE_LIST
            ApiField('words_learned', dtype=TYPE_STR, required=True),
            ApiField('to_repeat', dtype=TYPE_STR, required=True),

            ApiField('game', dtype=TYPE_STR, required=True)

        ],
        additional_fields = False
    )
)

register(
    ApiCall(
        identifier = 'GET /api/users/<email>/stats',
        url = '/api/users/{0}/stats'.format(TEST_EMAIL),
        method = METHOD_GET,
        auth = AUTH_USER_KEY,
        fields = [],
        additional_fields = False
    )
)

register(
    ApiCall(
        identifier = 'GET /api/ping',
        url = '/api/ping',
        method = METHOD_GET,
        auth = AUTH_API_KEY,
        fields = [],
        additional_fields = False
    )
)

register(
    ApiCall(
        identifier = 'PUT /api/users/<email>',
        url = '/api/users/{0}'.format(TEST_EMAIL),
        method = METHOD_PUT,
        auth = AUTH_USER_KEY,
        fields = [],
        additional_fields = True
    )
)

register(
    ApiCall(
        identifier = 'GET /api/users/<email>',
        url = '/api/users/{0}'.format(TEST_EMAIL),
        method = METHOD_GET,
        auth = AUTH_USER_KEY,
        fields = [],
        additional_fields = True
    )
)

register(
    ApiCall(
        identifier = 'GET /api/users/<email>/password',
        url = '/api/users/{0}/password'.format('monster@language-monster.com'),
        method = METHOD_GET,
        auth = AUTH_DEVICE_KEY,
        fields = [],
        additional_fields = True
    )
)

register(
    ApiCall(
        identifier = 'PUT /api/users/language',
        url = '/api/users/language',
        method = METHOD_PUT,
        auth = AUTH_USER_KEY,
        fields = [
            ApiField('language', dtype=TYPE_STR, required=True),
            ApiField('country', dtype=TYPE_STR, required=True),
        ],
        additional_fields = False
    )
)

register(
    ApiCall(
        identifier = 'PUT /api/users/email',
        url = '/api/users/email',
        method = METHOD_PUT,
        auth = AUTH_USER_KEY,
        fields = [
            ApiField('email', dtype=TYPE_STR, required=True),
        ],
        additional_fields = False
    )
)
