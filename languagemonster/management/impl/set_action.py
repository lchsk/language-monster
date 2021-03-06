import json

from core.models import (
    DataSet,
    DS2WP,
)
from core.data.language_pair import LANGUAGE_PAIRS_FLAT

def export_words(request, dataset_id, context):
    exported_values = _get_words_from_request(request, dataset_id)

    context['count'] = len(exported_values)
    context['data'] = json.dumps(exported_values)

def export_words_as_table(request, dataset_id, context):
    exported_values = _get_words_from_request(request, dataset_id)

    dataset = DataSet.objects.filter(id=dataset_id).first()

    if not dataset:
        raise RuntimeError('Set does not exist: %d', dataset_id)

    context['count'] = len(exported_values)

    pair = LANGUAGE_PAIRS_FLAT[dataset.lang_pair]

    data = [
        u'<tr><td>{base}</td><td>{target}</td></tr>\n'.format(
            base=word['ebase'],
            target=word['etarget'],
        )
        for word in exported_values
    ]

    table = u"""
<table class="vocabulary table table-striped">
    <th>{base}</th><th>{target}</th>
    {data}
</table>
    """.format(
        base=pair.base_language.original_name,
        target=pair.target_language.original_name,
        data='    '.join(data),
    )

    context['data'] = table

def export_metadata(ds):
    return dict(
        from_exported_file=True,
        icon=ds.icon,
        learners=ds.learners,
        name_base=ds.name_base,
        name_en=ds.name_en,
        name_target=ds.name_target,
        lang_pair=ds.lang_pair,
        pos=ds.pos,
        reversed_set=ds.reversed_set,
        simple_dataset=ds.simple_dataset,
        slug=ds.slug,
        visible=ds.visible,
        word_count=ds.word_count,
    )

def get_words_for_export(words):
    return [
        dict(
            ebase=w.wp.base,
            etarget=w.wp.target,
            pos=w.wp.pos,
        )
        for w in words
    ]

def export_set(request, dataset_id, context):
    exported_values = _get_words_from_request(request, dataset_id)
    ds = DataSet.objects.filter(pk=dataset_id).first()

    if ds:
        metadata = dict(
            from_exported_file=True,
            icon=ds.icon,
            learners=ds.learners,
            name_base=ds.name_base,
            name_en=ds.name_en,
            name_target=ds.name_target,
            lang_pair=ds.lang_pair,
            pos=ds.pos,
            reversed_set=ds.reversed_set,
            simple_dataset=ds.simple_dataset,
            slug=ds.slug,
            visible=ds.visible,
            word_count=ds.word_count,
        )

        data = dict(
            words=exported_values,
            metadata=metadata,
        )

        context['count'] = len(exported_values)
        context['data'] = json.dumps(data)

def update_set(request, dataset_id):
    all_ids = request.POST.getlist('word_pairs')
    to_remove = request.POST.getlist('remove')
    vis_ids = request.POST.getlist('check_vis')

    wps_to_hide = set(wp for wp in set(all_ids) - set(vis_ids))

    name_en = request.POST.get('name_en', 'name_en')
    name_base = request.POST.get('name_base', 'name_base')
    name_target = request.POST.get('name_target', 'name_target')
    icon = request.POST.get('icon', '')
    visible = request.POST.get('visible') is not None
    lowercase_target = request.POST.get('lowercase_target') is not None

    ds = DataSet.objects.filter(id=dataset_id).first()
    wp_tmp = DS2WP.objects.filter(ds=ds)
    pairs = [i.wp for i in wp_tmp]

    word_count = 0

    for p in pairs:
        if str(p.id) in to_remove:
            # DO NOT delete a word pair. Instead: unlink word pair from
            # a data set
            to_be_removed = DS2WP.objects.filter(wp=p, ds=ds).first()
            to_be_removed.delete()
        else:
            p.visible = str(p.id) not in wps_to_hide

            # Update
            _id = str(p.id)
            key_base = '{0}_base'.format(p.id)
            key_target = '{0}_target'.format(p.id)

            if key_base in request.POST and key_target in request.POST:
                p.base = request.POST[key_base]
                p.target = request.POST[key_target]
                p.pos = p.pos.strip()

                if lowercase_target:
                    p.target = p.target.lower()

                word_count += 1

            p.save()

    if ds:
        ds.word_count = word_count
        ds.name_en = name_en
        ds.name_base = name_base
        ds.name_target = name_target
        ds.visible = visible
        ds.icon = icon
        ds.save()

def _get_words_from_request(request, dataset_id):
    pairs = [
        i.wp
        for i in DS2WP.objects.filter(ds__id=dataset_id).select_related('wp')
        if i.wp.visible
    ]

    to_export = [
        dict(
            ebase=p.base,
            etarget=p.target,
            pos=p.pos,
        )
        for p in pairs
    ]

    return to_export
