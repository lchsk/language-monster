from __future__ import absolute_import
import logging

from django.conf import settings

from celery import shared_task

from core.models import (
    DataSet,
    DS2WP,
)

from celery.utils.log import get_task_logger

logger = logging.getLogger(__name__)


@shared_task
def sync_word_counts():
    '''
        Task counts number of words in every data set.
    '''

    datasets = DataSet.objects.all()

    for ds in datasets:
        ds.word_count = DS2WP.objects.filter(ds=ds).count()
        ds.save()
