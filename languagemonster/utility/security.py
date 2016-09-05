import os
import hashlib

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

def get_secure_hash():
    rand = os.urandom(32).encode('hex')

    return hashlib.sha512(rand).hexdigest()

def validate_password(request, password1, password2, messages):
    valid = True

    if len(password1) < 8:
        messages.add_message(
            request,
            messages.WARNING,
            _('msg_password_min_8_chars'),
        )
        valid = False

    if password1 != password2:
        messages.add_message(
            request,
            messages.WARNING,
            _('msg_passwords_dont_match'),
        )
        valid = False

    return valid
