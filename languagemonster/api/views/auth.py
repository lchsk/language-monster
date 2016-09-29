import logging

from core.data.base_language import BASE_LANGUAGES
from core.impl.user import (
    authenticate_user,
    register,
)

from api.serializers import (
    UserRegistrationRequest,
    UserLoginRequest,
    UserLoginResponse,
)
from api.views.base import APIAuthView

logger = logging.getLogger(__name__)

class UserRegistration(APIAuthView):
    def post(self, request):
        input_data = UserRegistrationRequest(data=request.data)

        if not input_data.is_valid():
            logger.warning('Invalid input')

            return self.failure('Invalid input', 400)

        base_language = input_data.validated_data['base_language']

        if base_language not in BASE_LANGUAGES:
            return self.failure('Invalid base language', 400)

        result, error_code, error_str = register(
            email=input_data.validated_data['email'],
            password1=input_data.validated_data['password'],
            password2=input_data.validated_data['password'],
            confirmation_required=False,
            base_language=BASE_LANGUAGES[base_language],
        )

        if result:
            return self.success({})
        else:
            return self.failure(error_code)


class UserLogin(APIAuthView):
    def post(self, request):
        input_data = UserLoginRequest(data=request.data)

        if not input_data.is_valid():
            logger.warning('Invalid input')

            return self.failure('Invalid input', 400)

        user = authenticate_user(
            email=input_data['email'].value,
            password=input_data['password'].value,
            new_hash=True,
        )

        if not user:
            logger.warning('Invalid email or password')

            return self.failure('Invalid email or password', 401)

        logger.info('Login successful: {}'.format(input_data['email']))

        resp = UserLoginResponse(data=dict(login_hash=user.api_login_hash))

        if not resp.is_valid():
            logger.warning('Internal error')

            return self.failure('Internal error', 500)

        return self.success(resp.data)
