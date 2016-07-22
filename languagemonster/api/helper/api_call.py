from rest_framework.response import Response

# API methods

METHOD_POST = 'POST'
METHOD_GET = 'GET'
METHOD_PUT = 'PUT'

# API authorization methods

AUTH_NO_AUTH = 'NO_AUTH'
AUTH_API_KEY = 'API_KEY'
AUTH_DEVICE_KEY = 'DEVICE_KEY'
AUTH_USER_KEY = 'USER_KEY'

# HTTP statuses

RESP_OK = 200
RESP_BAD_REQ = 400
RESP_UNAUTH = 401
RESP_NOT_FOUND = 404
RESP_METHOD_NOT_ALLOWED = 405
RESP_SERV_ERR = 500

# Data types
TYPE_STR = str
TYPE_INT = int
TYPE_FLOAT = float


def error(code=RESP_SERV_ERR, message=''):
    """
        returns an error response
    """

    resp = {
        'status': 'error',
        'data': {
            'message': message
        }
    }

    # TODO: check why json.dumps(resp) does not always work
    return Response(resp, code)


def success(data):
    """
        returns a success response
    """

    resp = {
        'status': 'success',
        'data': data
    }

    # TODO: check why json.dumps(resp) does not always work
    return Response(resp, RESP_OK)


class ApiField(object):
    """
        defines a single field inside an API call
    """

    def __init__(self, name, dtype=TYPE_STR, required=True):
        self.name = name
        self.dtype = dtype
        self.required = required


class ApiCall(object):
    """
        defines an api call
    """

    def __init__(
        self,
        identifier,
        url,
        method=METHOD_GET,
        auth=AUTH_API_KEY,
        fields=[],
        additional_fields=True
    ):
        self.identifier = identifier
        self.url = url
        self.method = method
        self.auth = auth
        self.fields = fields
        self.additional_fields = additional_fields
