from post_office import mail
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from utility.interface import *
from django.template.loader import get_template

EMAILS = {
    # User emails

    'welcome': {
        'filename': 'welcome.html',
        'subject': _('mail_subj_welcome'),
    },
    'email_change': {
        'filename': 'email_change.html',
        'subject': _('mail_subj_confirm_email'),
    },
    'password_recovery': {
        'filename': 'password_recovery.html',
        'subject': _('mail_subj_new_password'),
    },

    # Admin stuff

    'contact_form': {
        'filename': 'contact_form.html',
        'subject': ('Message from Contact Form')
    },
    'test_email': {
        'filename': 'test_email.html',
        'subject': ('Language Monster Test Email')
    }
}


def send_template_email(request, recipient, template, ctx):
    """
        General function to be called for sending emails
    """

    body = get_template('emails/' + EMAILS[template]['filename']).render(
        ctx
    )

    mail.send(
        recipient,
        settings.EMAIL_FROM,
        subject=EMAILS[template]['subject'],
        html_message=body,
    )
