from collections import defaultdict

from django.shortcuts import render

from core.models import (
    DataSet,
)

from core.language_pair import LANGUAGE_PAIRS_ALL

from utility.interface import (
    get_context,
    landing_language,
)

def info(request):
    print 'hello'

def index(request):
    ctx = get_context(request)

    ctx['language'] = landing_language(request)

    import json

    acronym = ctx['language'].language.acronym

    # Serialize

    langs = []

    for symbol, lang in LANGUAGE_PAIRS_ALL[acronym].iteritems():
        langs.append(
            dict(
                symbol=symbol,
                base_language=dict(
                    english_name=lang.base_language.english_name,
                    original_name=lang.base_language.original_name,
                    acronym=lang.base_language.acronym,
                    slug=lang.base_language.slug,
                    image_filename=lang.base_language.image_filename,
                    flag_filename=lang.base_language.flag_filename,
                ),
                target_language=dict(
                    english_name=lang.target_language.english_name,
                    original_name=lang.target_language.original_name,
                    acronym=lang.target_language.acronym,
                    slug=lang.target_language.slug,
                    image_filename=lang.target_language.image_filename,
                    flag_filename=lang.target_language.flag_filename,
                ),
            )
        )

    datasets_db = DataSet.objects.filter(
        visible=True
    )

    datasets = defaultdict(list)

    for d in datasets_db:
        base, target = d.lang_pair.split('_')

        if acronym == base:
            datasets[target].append(dict(
                id=d.id,
                name_en=d.name_en,
                name_base=d.name_base,
                name_target=d.name_target,
                slug=d.slug,
                icon=d.icon,
                lang_pair=d.lang_pair,
                simple=d.simple_dataset,
            ))

    ctx['langs'] = json.dumps(langs)
    ctx['datasets'] = json.dumps(datasets)

    return render(request, 'light/content.html', ctx)
