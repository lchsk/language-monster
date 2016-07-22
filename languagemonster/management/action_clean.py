# -*- coding: utf-8 -*-
import logging

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.conf import settings

from utility.interface import get_context

from core.models import *

logger = logging.getLogger(__name__)
settings.LOGGER(logger, settings.LOG_WORKERS_HANDLER)

@login_required
@staff_member_required
def remove_dangling_words(request):
    c = get_context(request)

    ids = request.POST.getlist('remove')

    for pk in ids:
        wp = WordPair.objects(pk=pk).first()

        if wp:
            wp.delete()

    return redirect(reverse('management:index'))