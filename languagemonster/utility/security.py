import uuid

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

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
