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
def simple_dataset_from(request, dataset_id):
    c = get_context(request)

    c['simple_datasets'] = SimpleDataset.objects.all()
    c['dataset_id'] = dataset_id

    return render(request, "app/management/form_simple_dataset_from.html", c)

@login_required
@staff_member_required
def generate_simple_dataset(request, dataset_id):
    c = get_context(request)

    ds = DataSet.objects(pk=dataset_id).first()
    simple_dataset_id = request.POST['simple_dataset_id']
    title = request.POST['title']
    base_or_target = request.POST['base_or_target']
    sds = SimpleDataset.objects(pk=simple_dataset_id).first()

    if ds and sds and base_or_target in ('base', 'target') and title:
        simple_def = sds.data.split('\n')
        simple_def = [ x.strip() for x in simple_def if x ]

        new_ds = DataSet(
            icon=ds.icon,
            name_base=ds.name_base,
            name_en=title,
            name_target=ds.name_target,
            pair=ds.pair,
            visible=False,
            word_count=0,
            pos=ds.pos,
            from_exported_file=ds.from_exported_file,
            simple_dataset=True
        )
        new_ds.save()

        wp_tmp = DS2WP.objects(ds=ds)
        word_pairs = [ x.wp for x in wp_tmp ]

        for wp in word_pairs:
            if getattr(wp, base_or_target, None) in simple_def:
                new_link = DS2WP(
                    ds = new_ds,
                    wp = wp
                )
                new_link.save()

    return redirect(reverse('management:index'))

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
