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
def view_copy_words_to(request, target_dataset_id):
    c = get_context(request)

    target_ds = DataSet.objects.filter(id=target_dataset_id).first()
    source_dataset_id = request.POST['source_dataset_id']
    source_ds = DataSet.objects.filter(id=source_dataset_id).first()

    if source_ds and target_ds and source_ds.pair == target_ds.pair:
        words_source_tmp = DS2WP.objects.filter(ds=source_ds)
        words_target_tmp = DS2WP.objects.filter(ds=target_ds)

        words_source = [x.wp for x in words_source_tmp]
        words_target = [x.wp for x in words_target_tmp]

        # present on both sets
        words_both = set()
        words_source_only = set()
        words_target_only = set()

        for ws in words_source:
            if ws in words_target:
                words_both.add(ws)
            else:
                words_source_only.add(ws)

        for wt in words_target:
            if wt not in words_source:
                words_target_only.add(wt)

        c['source_ds'] = source_ds
        c['target_ds'] = target_ds
        c['words_both'] = words_both
        c['words_source_only'] = words_source_only
        c['words_target_only'] = words_target_only

        return render(request, "app/management/form_copy_words_to.html", c)
    return redirect(reverse('management:index'))
