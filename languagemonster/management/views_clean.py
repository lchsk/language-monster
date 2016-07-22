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
def view_dangling_word_pairs(request):

    c = get_context(request)

    all_words = WordPair.objects.all()

    c['count'] = len(all_words)

    dangling = []

    for w in all_words:
        link = DS2WP.objects.filter(wp=w).first()
        if not link:
            dangling.append(w)

    c['dangling'] = dangling

    return render(request, "app/management/view_dangling_word_pairs.html", c)
