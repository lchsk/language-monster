import uuid
import hmac

from django.conf import settings
from core.models import (
    OpenGameSession,
)


def get_hash_pair(key, value):
    return hmac.new(key, value).hexdigest()


def check_game_session(game_session_id):
    game_session_obj = OpenGameSession.objects.filter(
        game_session_id=game_session_id
    ).first()

    if not game_session_obj:
        return False

    return game_session_obj.game_token == hmac.new(
        settings.GAME_SESSION_KEY,
        game_session_id
    ).hexdigest()


def create_game_session_hash(user, dataset):
    """
        Creates new hash pair for game session
        (needed) for API calls froms JS
        - should be used together with check_game_session()
    """

    game_session_id = uuid.uuid4().hex

    game_token = hmac.new(
        settings.GAME_SESSION_KEY,
        game_session_id
    ).hexdigest()

    open_session = OpenGameSession(
        game_session_id=game_session_id,
        game_token=game_token,
        user=user,
        dataset=dataset
    )
    open_session.save()

    return game_session_id

def validate_password(request, password1, password2, messages):
    valid = True

    if len(password1) < 8:
        messages.add_message(
            request,
            messages.WARNING,
            _("New password must be at least 8 characters long.")
        )
        valid = False

    if password1 != password2:
        messages.add_message(
            request,
            messages.WARNING,
            _("Passwords don't match.")
        )
        valid = False

    return valid
