# -*- coding: utf-8 -*-
import logging
import os
import re
import json
import datetime
from difflib import SequenceMatcher

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import Http404

from core.models import *
from utility.interface import *
from management.impl.security import *

from management.impl.stats import get_status_data

from core.data.language_pair import (
    LANGUAGE_PAIRS_FLAT,
    LANGUAGE_PAIRS,
    get_language_pair,
)

from utility.views import (
    ContextView,
    AuthContextView,
    SuperUserContextView,
    NoTemplateMixin,
)

from management.impl.set_action import (
    export_words,
    export_set,
    update_set,
)

from management.impl.util import parse_line

logger = logging.getLogger(__name__)
settings.LOGGER(logger, settings.LOG_WORKERS_HANDLER)

class IndexView(SuperUserContextView):
    template_name = 'app/management/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        return context

def _parse_line(line):
    """
        takes data from a line
    """

    line = line.split('||')

    columns = 5

    assert len(line) == columns, 'Invalid format: should be {0} columns'.format(columns)

    # base, target, english, comments

    base_en, target_en = '', ''
    b, t, pop, en, c = line[0], line[1], line[2], line[3], line[4]
    from_english = '{{from_english}}' in c
    english_invalid = '{{english_invalid}}' in c
    verified = '{{verified}}' in c

    # r = re.findall(r'.*?\{(.+?)=(.+?)\}.*?', c)
    # from this: {{english_invalid}}{base=viper}{target=otter}{{something_some}}
    # produces: ['english_invalid', 'base=viper', 'target=otter', 'something_some']
    r = re.findall(r'\{([^{}]+)\}', c)

    for pair in r:
        tmp = pair.split('=')

        if len(tmp) != 2:
            continue

        if tmp[0] == 'base':
            base_en = tmp[1]
        elif tmp[0] == 'target':
            target_en = tmp[1]

    # for k, v in r:
    #     if k == 'base':
    #         base_en = v
    # 
    #     if k == 'target':
    #         target_en = v

    pair = dict(
        b = b.strip(),
        t = t.strip(),
        en = en,
        c = c,
        base_en = base_en,
        target_en = target_en,
        from_english = from_english,
        english_invalid = english_invalid,
        verified = verified,
        pop = pop
    )

    return pair

class AddNewSetView(SuperUserContextView):
    template_name = 'app/management/add_set.html'

    def get_context_data(self, **kwargs):
        context = super(AddNewSetView, self).get_context_data(**kwargs)

        path = self.kwargs['path']

        if os.path.exists(path):
            f = open(path)

            metadata = {}
            correct = True
            error_msg = ''
            exists = False
            words = 0

            w = []

            for line in f:
                if line.startswith('#'):
                    if '=' in line[1:]:
                        info = line[1:].strip().split('=')

                        if len(info) == 2:
                            metadata[info[0]] = info[1]
                elif '||' in line:
                    words += 1

                    pair = _parse_line(line)

                    w.append(pair)

            lang_pair = get_language_pair(
                metadata['base'],
                metadata['target']
            )

            ds = DataSet.objects.filter(
                lang_pair=lang_pair.symbol,
                name_en=metadata['name_en']
            ).first()

            if ds:
                exists = True

            if not metadata['name_en']:
                correct = False
                error_msg = 'name_en is missing'

            context['path'] = path
            context['exists'] = exists
            context['correct'] = correct
            context['error_msg'] = error_msg
            context['pair'] = lang_pair
            context['name_en'] = metadata['name_en']
            context['pos'] = metadata.get('pos')
            context['from_exported_file'] = metadata.get(
                'from_exported_file',
                False
            )
            context['words'] = words
            context['wordlist'] = w

            f.close()
        else:
            raise Http404

        return context

class DoSaveNewSet(SuperUserContextView):
    template_name = 'app/management/index.html'

    def get_context_data(self, **kwargs):
        context = super(DoSaveNewSet, self).get_context_data(**kwargs)

        return context

    def post(self, *args, **kwargs):
        path = self.kwargs['path']
        request = self.request

        f = open(path)

        words = int(request.POST['words'])
        icon = request.POST['icon']
        name_en = request.POST['name_en']
        name_base = request.POST['name_base']
        name_target = request.POST['name_target']
        base_acronym = request.POST['base']
        target_acronym = request.POST['target']
        pos = request.POST['pos']
        from_exported_file = request.POST.get('from_exported_file', False)

        lang_pair = get_language_pair(base_acronym, target_acronym)

        if lang_pair and words > 0 and name_en:
            # Add new object
            ds = DataSet(
                icon=icon,
                name_base=name_base,
                name_en=name_en,
                name_target=name_target,
                lang_pair=lang_pair.symbol,
                visible=False,
                word_count=words,
                pos=pos,
                from_exported_file=from_exported_file,
                simple_dataset=False
            )
            ds.save()

            # Warning!
            # Adding actual word pairs into DB

            for i, line in enumerate(f):
                if line[0] != '#' and '||' in line:

                    p = parse_line(line)

                    wp = WordPair(
                        base=p['b'],
                        target=p['t'],
                        index=i,
                        english=p['en'],
                        comments=p['c'],
                        english_invalid=p['english_invalid'],
                        base_en=p['base_en'],
                        target_en=p['target_en'],
                        from_english=p['from_english'],
                        verified=p['verified'],
                        pos=pos,
                        pop=p['pop']
                    )
                    wp.save()

                    link = DS2WP(
                        wp=wp,
                        ds=ds
                    )
                    link.save()

        f.close()

        messages.add_message(
            request,
            messages.SUCCESS,
            'New set added',
        )

        return self.redirect('management:index')

class SetsView(SuperUserContextView):
    template_name = 'app/management/sets.html'

    def get_context_data(self, **kwargs):
        context = super(SetsView, self).get_context_data(**kwargs)

        show_sets_option = self.request.GET.get('show_sets', 0)
        language_pair = self.request.GET.get('language_pair')

        if language_pair:
            sets = DataSet.objects.filter(
                lang_pair=language_pair
            ).order_by('-date_added')
        else:
            sets = DataSet.objects.all().order_by('-date_added')

        if int(show_sets_option) == 1:
            sets = filter(lambda x: x.simple_dataset, sets)
        elif int(show_sets_option) == 2:
            sets = filter(lambda x: not x.simple_dataset, sets)

        context['show_sets'] = [
            (0, 'All kinds'),
            (1, 'Basic sets only'),
            (2, 'Full sets only'),
        ]
        context['show_sets_option'] = int(show_sets_option)

        context['language_pair'] = language_pair
        context['sets'] = sets
        context['pairs'] = sorted(LANGUAGE_PAIRS_FLAT)

        return context

class EditSetView(SuperUserContextView):
    template_name = 'app/management/edit_set.html'

    def get_context_data(self, **kwargs):
        context = super(EditSetView, self).get_context_data(**kwargs)

        dataset = DataSet.objects.filter(
            pk=kwargs['dataset_id']
        ).first()

        if dataset:
            sort_by = self.request.GET.get('sort_by', 'base')
            sort_ord = self.request.GET.get('sort_ord', 'DESC')
            reverse = sort_ord == 'DESC'

            wp_tmp = DS2WP.objects.filter(ds=dataset).select_related('wp')
            all_words = [i.wp for i in wp_tmp]

            for i in all_words:
                i.comments = re.sub(r'{base=(.*?)}', '', i.comments)
                i.comments = re.sub(r'{target=(.*?)}', '', i.comments)

            # different format here
            words = mark_suspicious_words(dataset, all_words)

            susp = [ i for i in words if i['susp'] ]
            clean = [ i for i in words if not i['susp'] ]

            if sort_by == 'baselen':
                susp = sorted(
                    susp,
                    key=lambda s: len(s['wp'].base),
                    reverse=reverse
                )
                clean = sorted(
                    clean,
                    key=lambda s: len(s['wp'].base),
                    reverse=reverse
                )
            else:
                susp = sorted(
                    susp,
                    key=lambda s: s['wp'].pop,
                    reverse=reverse
                )
                clean = sorted(
                    clean,
                    key=lambda s: s['wp'].pop,
                    reverse=reverse
                )

            context['clean'] = clean
            context['susp'] = susp

            clean_cnt = len(clean)
            susp_cnt = len(susp)
            clean_zero_cnt = len([i for i in clean if i['wp'].pop == 0])
            susp_zero_cnt = len([i for i in susp if i['wp'].pop == 0])

            context['stats'] = dict(
                clean=clean_cnt,
                susp=susp_cnt,
                susp_zero=susp_zero_cnt,
                clean_zero=clean_zero_cnt,
                all = clean_cnt + susp_cnt
            )

            context['words'] = words
            context['ds'] = dataset
        else:
            raise Http404

        return context

@require_superuser
def import_diff(request, dataset_id):

    c = get_context(request)

    error = None
    remote_data = None
    local_data = []

    try:
        # data brought from somewhere else
        remote_data = json.loads(request.POST['data'])

        # local data
        ds = DataSet.objects(id=dataset_id).first()
        # pairs = WordPair.objects(data_set=ds)
        wp_tmp = DS2WP.objects.filter(ds=ds)
        pairs = [i.wp for i in wp_tmp]

        for p in pairs:
            item = {}

            # local
            item['id'] = str(p.id)
            item['lbase'] = p.base
            item['ltarget'] = p.target

            local_data.append(item)
    except:
        error = 'JSON invalid'

    single_list = []
    the_same = 0
    not_the_same = 0

    for remote in remote_data:
        for local in local_data:
            if remote['ebase'] == local['lbase']:
                item = dict(
                    id = local['id'],
                    ebase = remote['ebase'],
                    etarget = remote['etarget'],
                    lbase = local['lbase'],
                    ltarget = local['ltarget'],
                )

                if item['etarget'] == item['ltarget']:
                    item['result'] = 1.0
                    the_same += 1
                else:
                    item['result'] = SequenceMatcher(
                        None,
                        item['etarget'],
                        item['ltarget'],
                    ).ratio()
                    not_the_same += 1
                single_list.append(item)

    c['ds'] = ds
    c['error'] = error
    c['data'] = single_list
    c['the_same'] = the_same
    c['not_the_same'] = not_the_same

    return render(request, "app/management/import_diff.html", c)

@require_superuser
def save_diff(request, dataset_id):

    c = get_context(request)

    ids = request.POST.getlist('checked')

    ds = DataSet.objects.filter(id=dataset_id).first()
    # pairs = WordPair.objects(data_set=ds)
    wp_tmp = DS2WP.objects.filter(ds=ds)
    pairs = [i.wp for i in wp_tmp]

    to_export = []

    for p in pairs:
        if str(p.id) in ids:
            _id = str(p.id)
            key_base = 'new_{0}_base'.format(p.id)
            key_target = 'new_{0}_target'.format(p.id)

            if key_base in request.POST \
            and key_target in request.POST:
                p.base = request.POST[key_base]
                p.target = request.POST[key_target]
                p.save()

    return redirect(reverse('management:index'))

class SetActionDispatch(SuperUserContextView):
    template_name = 'app/management/export.html'

    def get_context_data(self, **kwargs):
        context = super(SetActionDispatch, self).get_context_data(**kwargs)

        return context

    def post(self, *args, **kwargs):
        ctx = self.get_context_data()

        request = self.request
        dataset_id = kwargs['dataset_id']

        if request.POST.get('update') == 'update':
            update_set(request, dataset_id)
            return self.redirect('management:index')
        elif request.POST.get('export') == 'export':
            self.template_name = 'app/management/export.html'
            export_words(request, dataset_id, ctx)
        elif request.POST.get('export_set') == 'export_set':
            self.template_name = 'app/management/export.html'
            export_set(request, dataset_id, ctx)
        elif request.POST.get('import') == 'import':
            self.template_name = 'app/management/import.html'

        return render(self.request, self.template_name, ctx)

class AddNewSetFromFileView(SuperUserContextView):
    template_name = 'app/management/add_new_set_from_file.html'

    def get_context_data(self, **kwargs):
        context = super(AddNewSetFromFileView, self).get_context_data(**kwargs)

        files = []
        sets = {}
        base_dir = os.path.join(settings.BASE_DIR, '../data/output/')

        for root, dirnames, filenames in os.walk(base_dir):
            if root and filenames:
                for file in filenames:
                    if os.path.exists(os.path.join(root, file)):
                        files.append(os.path.join(root, file))

        for f in files:
            sp = f.replace(base_dir, '').split('/')
            current = sets
            length = len(sp)

            for i, element in enumerate(sp):
                if i == length - 1:
                    current[element] = f
                else:
                    if element not in current:
                        current[element] = {}
                    current = current[element]

        context['sets'] = sets

        return context

@require_superuser
def clean(request):
    '''Cleans rubbish from the database'''

    c = get_context(request)

    logger.info("Starting cleanup")

    a = UserResult.objects.all()

    c = 0

    # TODO: ?
    # for i in a:
    #     if isinstance(i.user, DBRef) or isinstance(i.data_set, DBRef):
    #         c += 1
    #         i.delete()

    logger.info("Removed %s UserResult instances", c)

    a = Progression.objects.all()

    c = 0

    # for i in a:
    #     if isinstance(i.user, DBRef) or isinstance(i.pair, DBRef):
    #         c += 1
    #         i.delete()

    logger.info("Removed %s Progression instances", c)

    #####################################
    # DS2WP (data set to word pair)
    #####################################

    # a = DS2WP.objects()
    # 
    # c = 0
    # 
    # for i in a:
    #     if isinstance(i.wp, DBRef) or isinstance(i.ds, DBRef):
    #         c += 1
    #         i.delete()

    logger.info("Removed %s DS2WP instances", c)

    # a = WordPair.objects()
    # 
    # c = 0
    # 
    # for i in a:
    #     if isinstance(i.data_set, DBRef):
    #         c += 1
    #         i.delete()
    # 
    # logger.info("Removed %s WordPair instances", c)

    # a = DataSet.objects()
    # 
    # c = 0
    # 
    # for i in a:
    #     if isinstance(i.pair, DBRef):
    #         c += 1
    #         i.delete()

    logger.info("Removed %s DataSet instances", c)

    # a = ErrorReport.objects()
    # 
    # c = 0
    # 
    # for i in a:
    #     if isinstance(i.user, DBRef) or isinstance(i.data_set, DBRef):
    #         c += 1
    #         i.delete()
    # 
    # logger.info("Removed %s ErrorReport instances", c)
    # 
    # a = UserWordPair.objects()
    # 
    # c = 0
    # 
    # for i in a:
    #     if isinstance(i.user, DBRef) or isinstance(i.word_pair, DBRef):
    #         c += 1
    #         i.delete()
    # 
    # logger.info("Removed %s UserWordPair instances", c)

    logger.info('Finished cleanup')

    return redirect(reverse('management:index'))

class DuplicatesView(SuperUserContextView):
    template_name = 'app/management/duplicates.html'

    def get_context_data(self, **kwargs):
        context = super(DuplicatesView, self).get_context_data(**kwargs)

        ds = DataSet.objects.filter(pk=kwargs['dataset_id']).first()
        wp_tmp = DS2WP.objects.filter(ds=ds)
        pairs = [i.wp for i in wp_tmp]

        suspected = []

        for i in pairs:
            for j in pairs:
                if i is not j:
                    ratio_base = SequenceMatcher(
                        None,
                        i.base,
                    j.base).ratio()
                    ratio_target = SequenceMatcher(
                        None,
                        i.target,
                        j.target
                    ).ratio()

                    ratio = ratio_base + ratio_target

                    if ratio >= 1.1 or ratio_base >= 0.7 or ratio_target >= 0.7:
                        item = dict(
                            base1=i.base,
                            base2=j.base,
                            target1=i.target,
                            target2=j.target,
                            ratio_base=ratio_base,
                            ratio_target=ratio_target,
                            ratio=ratio
                        )

                        suspected.append(item)

        suspected = {
            x['ratio']:
            x for x in suspected
        }.values()

        suspected = sorted(
            suspected,
            key=lambda x: x['ratio'],
            reverse=True
        )

        context['suspected'] = suspected
        context['ds'] = ds

        return context

class StatusView(SuperUserContextView):
    template_name = 'app/management/status.html'

    def get_context_data(self, **kwargs):
        context = super(StatusView, self).get_context_data(**kwargs)

        context['data'] = get_status_data()

        return context

@require_superuser
def copy_and_reverse(request, dataset_id):
    """
    Create another set but inverse base <-> target in word pairs
    """

    ds = DataSet.objects.filter(pk=dataset_id).first()

    if not ds:
        raise Exception("Data set does not exist")

    pair = ds.pair

    new_pair = LanguagePair.objects.filter(
        base_language=pair.target_language,
        target_language=pair.base_language
    ).first()

    if not new_pair:
        raise Exception("Reverse for {0} does not exist!".format(str(pair)))

    new_ds = DataSet(
        icon=ds.icon,
        name_base=ds.name_target,
        name_en=ds.name_en,
        name_target=ds.name_base,
        pair=new_pair,
        visible=False,
        word_count=ds.word_count,
        pos = ds.pos,
        from_exported_file = ds.from_exported_file,
        simple_dataset=False
    )
    new_ds.reversed_set = True
    new_ds.save()

    wp_links = DS2WP.objects.filter(ds=ds)

    for link in wp_links:
        wp_ = link.wp

        exists = WordPair.objects.filter(base=wp_.target, target=wp_.base).first()

        if exists:
            new_link = DS2WP(
                wp=exists,
                ds=new_ds
            )
            new_link.save()
        else:
            new_wp = WordPair(
                base=wp_.target,
                target=wp_.base,
                base_en=wp_.target_en,
                target_en=wp_.base_en,
                english=wp_.english,
                comments=wp_.comments,
                pos=wp_.pos,
                english_invalid=wp_.english_invalid,
                from_english=wp_.from_english,
                verified=wp_.verified,
                index=wp_.index,
                pop=wp_.pop
            )
            new_wp.save()
            new_link = DS2WP(
                wp=new_wp,
                ds=new_ds
            )
            new_link.save()

    return redirect(reverse('management:index'))

class ImportSetView(SuperUserContextView):
    template_name = 'app/management/import.html'

    def get_context_data(self, **kwargs):
        context = super(ImportSetView, self).get_context_data(**kwargs)

        context['dataset_id'] = None

        return context

class DoImportSet(SuperUserContextView):
    template_name = 'app/management/index.html'

    def get_context_data(self, **kwargs):
        context = super(DoImportSet, self).get_context_data(**kwargs)

        return context

    def post(self, *args, **kwargs):
        request = self.request

        error = None
        remote_data = None

        try:
            remote_data = json.loads(request.POST['data'])
            words = remote_data['words']
            metadata = remote_data['metadata']
        except:
            error = 'JSON invalid'

        if not error:
            set_exists = DataSet.objects.filter(
                name_en=metadata['name_en']
            ).first()

            pair = metadata['pair']

            base = Language.objects.filter(acronym=pair['base']).first()
            target = Language.objects.filter(acronym=pair['target']).first()

            language_pair = LanguagePair.objects.filter(
                base_language=base,
                target_language=target
            ).first()

            if set_exists:
                error = 'Data set ({0}) already exists'.format(
                    metadata['name_en']
                )
            elif not language_pair:
                error = 'Language Pair does not exist ({0} -> {0})'.format(
                    pair['base'],
                    pair['target']
                )
            else:
                # Validation passed: actually adding data

                imported_ds = DataSet(
                    from_exported_file=metadata['from_exported_file'],
                    icon=metadata['icon'],
                    learners=metadata['learners'],
                    name_base=metadata['name_base'],
                    name_en=metadata['name_en'],
                    name_target=metadata['name_target'],
                    pair=language_pair,
                    pos=metadata['pos'],
                    reversed_set=metadata['reversed_set'],
                    simple_dataset=metadata['simple_dataset'],
                    slug=metadata['slug'],
                    visible=False,
                    word_count=metadata['word_count'],
                )

                imported_ds.save()

                datasets = DataSet.objects.filter(pair=language_pair).all()

                # Checking if word already exists in the DB

                for wp in words:
                    wp_obj = None

                    for ds in datasets:
                        links = DS2WP.objects.filter(
                            ds=ds
                        )

                        for link in links:
                            if all((
                                link.wp.base == wp['ebase'],
                                link.wp.target == wp['etarget']
                            )):
                                wp_obj = link.wp
                                break

                        if wp_obj:
                            break

                    if not wp_obj:
                        # Word doesn't exist in the DB, we need to add it
                        logger.info('adding word %s' % str(wp_obj))
                        wp_obj = WordPair(
                            base=wp['ebase'],
                            target=wp['etarget'],
                            pair=language_pair
                        )
                        wp_obj.save()

                    # Add new link
                    if wp_obj:
                        logger.info('adding link %s' % str(wp_obj))
                        new_link = DS2WP(
                            ds=imported_ds,
                            wp=wp_obj
                        )
                        new_link.save()

        if error:
            messages.add_message(
                request,
                messages.WARNING,
                error,
            )
        else:
            messages.add_message(
                request,
                messages.WARNING,
                'Success',
            )

        return self.redirect('management:index')

@require_superuser
def do_import_set(request):
    """
        Save imported set (metadata + words)
    """

    c = get_context(request)

    error = None
    remote_data = None

    try:
        remote_data = json.loads(request.POST['data'])
        words = remote_data['words']
        metadata = remote_data['metadata']
    except:
        error = 'JSON invalid'

    if not error:
        set_exists = DataSet.objects.filter(
            name_en=metadata['name_en']
        ).first()

        pair = metadata['pair']

        base = Language.objects.filter(acronym=pair['base']).first()
        target = Language.objects.filter(acronym=pair['target']).first()

        language_pair = LanguagePair.objects.filter(
            base_language=base,
            target_language=target
        ).first()

        if set_exists:
            error = 'Data set ({0}) already exists'.format(metadata['name_en'])
        elif not language_pair:
            error = 'Language Pair does not exist ({0} -> {0})'.format(
                pair['base'],
                pair['target']
            )
        else:
            # Validation passed: actually adding data

            imported_ds = DataSet(
                from_exported_file=metadata['from_exported_file'],
                icon=metadata['icon'],
                learners=metadata['learners'],
                name_base=metadata['name_base'],
                name_en=metadata['name_en'],
                name_target=metadata['name_target'],
                pair=language_pair,
                pos=metadata['pos'],
                reversed_set=metadata['reversed_set'],
                simple_dataset=metadata['simple_dataset'],
                slug=metadata['slug'],
                # it's better if it requires manual changing to visible
                # visible=metadata['visible'],
                visible=False,
                word_count=metadata['word_count'],
            )
            imported_ds.save()

            datasets = DataSet.objects.filter(
                pair=language_pair
            ).all()

            # Checking if word already exists in the DB

            for wp in words:

                wp_obj = None

                for ds in datasets:
                    links = DS2WP.objects.filter(
                        ds=ds
                    )

                    for link in links:
                        if all((
                            link.wp.base == wp['ebase'],
                            link.wp.target == wp['etarget']
                        )):
                            wp_obj = link.wp
                            break

                    if wp_obj:
                        break

                if not wp_obj:
                    # Word doesn't exist in the DB, we need to add it
                    logger.info('adding word %s' % str(wp_obj))
                    wp_obj = WordPair(
                        base=wp['ebase'],
                        target=wp['etarget'],
                        pair=language_pair
                    )
                    wp_obj.save()

                # Add new link
                if wp_obj:
                    logger.info('adding link %s' % str(wp_obj))
                    new_link = DS2WP(
                        ds=imported_ds,
                        wp=wp_obj
                    )
                    new_link.save()

    if error:
        c['error'] = error
        return render(request, "app/management/import.html", c)

    return redirect(reverse('management:index'))
