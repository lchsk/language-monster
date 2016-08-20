from __future__ import absolute_import
import logging

from celery import shared_task

from django.conf import settings
from django.core.management import call_command
from core.models import (
    MonsterUser,
)

import core.impl.mail as mail

logger = logging.getLogger(__name__)
settings.LOGGER(logger, settings.LOG_WORKERS_HANDLER)


@shared_task
def send_queued_mail():
    with open(settings.LOG_MAIL_FILE) as f:
        call_command('send_queued_mail', stdout=f, stderr=f)


@shared_task
def send_test_email():

    user_count = MonsterUser.objects.count()

    logger.info('Sending a test email...')

    mail.send_template_email(
        request=None,
        recipient=settings.EMAIL_FROM,
        template='test_email',
        ctx={
            'USER_COUNT': user_count,
        }
    )

    logger.info('Test email sent')
