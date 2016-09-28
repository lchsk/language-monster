# -*- coding: utf-8 -*-
"""Management views"""

import logging
import os
import re
import json
from difflib import SequenceMatcher

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import (
    render,
    redirect,
)
from django.conf import settings
from django.http import Http404

from core.models import (
    DataSet,
    SimpleDataset,
    WordPair,
    DS2WP,
)
from utility.interface import (
    get_context,
)
from management.impl.security import (
    mark_suspicious_words,
    require_superuser,
)

from management.impl.stats import get_status_data

from core.data.language_pair import (
    LANGUAGE_PAIRS_FLAT,
    get_language_pair,
)

from utility.views import SuperUserContextView

from management.impl.set_action import (
    export_words,
    export_set,
    update_set,
)

from management.impl.util import parse_line

logger = logging.getLogger(__name__)

class IndexView(SuperUserContextView):
    template_name = 'app/management/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        return context

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

                    pair = parse_line(line)

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

            all_words = DS2WP.objects.filter(
                ds__lang_pair=lang_pair.symbol
            ).select_related('wp', 'ds')

            for i, line in enumerate(f):
                if line[0] != '#' and '||' in line:
                    current_word_pair = None
                    p = parse_line(line)

                    for word in all_words:
                        if all((
                            p['b'] == word.wp.base,
                            p['t'] == word.wp.target,
                            p['en'] == word.wp.english,
                        )):
                            current_word_pair = word.wp
                            break

                    if current_word_pair:
                        wp = current_word_pair
                    else:
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
                            pop=p['pop'],
                        )

                        wp.save()

                    link = DS2WP(
                        wp=wp,
                        ds=ds,
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
                lang_pair=language_pair,
                status='A',
            ).order_by('-date_added')
        else:
            sets = DataSet.objects.filter(status='A').order_by('-date_added')

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

class DoRemoveDataset(SuperUserContextView):
    def get(self, *args, **kwargs):
        dataset_id = self.kwargs['dataset_id']

        dataset = DataSet.objects.filter(pk=dataset_id).first()

        if not dataset:
            raise Http404

        dataset.status = 'X'
        dataset.save()

        return self.redirect_with_success(
            'management:sets',
            'Data set removed',
        )

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

            susp = [i for i in words if i['susp']]
            clean = [i for i in words if not i['susp']]

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
                all=clean_cnt + susp_cnt,
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
                    id=local['id'],
                    ebase=remote['ebase'],
                    etarget=remote['etarget'],
                    lbase=local['lbase'],
                    ltarget=local['ltarget'],
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
                        j.base,
                    ).ratio()
                    ratio_target = SequenceMatcher(
                        None,
                        i.target,
                        j.target,
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
                            ratio=ratio,
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

class DoCopyAndReverse(SuperUserContextView):
    def get(self, *args, **kwargs):
        ds = DataSet.objects.filter(pk=self.kwargs['dataset_id']).first()

        if not ds:
            raise Http404

        base, target = ds.pair.symbol.split('_')

        new_pair = '{}_{}'.format(target, base)

        new_ds = DataSet(
            icon=ds.icon,
            name_base=ds.name_target,
            name_en=ds.name_en,
            name_target=ds.name_base,
            lang_pair=new_pair,
            visible=False,
            word_count=ds.word_count,
            pos=ds.pos,
            from_exported_file=ds.from_exported_file,
            simple_dataset=False
        )

        new_ds.reversed_set = True
        new_ds.save()

        wp_links = DS2WP.objects.filter(ds=ds)

        for link in wp_links:
            wp_ = link.wp

            exists = WordPair.objects.filter(
                base=wp_.target,
                target=wp_.base,
            ).first()

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

        return self.redirect_with_success(
            'management:index',
            'Data set copied and reversed',
        )

class ImportSetView(SuperUserContextView):
    template_name = 'app/management/import.html'

    def get_context_data(self, **kwargs):
        context = super(ImportSetView, self).get_context_data(**kwargs)

        context['dataset_id'] = None

        return context

# TODO: to fix?
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
                error = 'Language Pair does not exist ({} -> {})'.format(
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
                        links = DS2WP.objects.filter(ds=ds)

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

# TODO: To be removed?
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

class DanglingWordPairsView(SuperUserContextView):
    template_name = 'app/management/view_dangling_word_pairs.html'

    def get_context_data(self, **kwargs):
        context = super(DanglingWordPairsView, self).get_context_data(**kwargs)

        all_words = WordPair.objects.all()
        all_links = DS2WP.objects.all()

        correct_words = {link.wp_id for link in all_links}

        dangling = []

        for w in all_words:
            if w.id not in correct_words:
                dangling.append(w)

        context['dangling'] = dangling
        context['count'] = len(all_words)

        return context

class DoRemoveDanglingWords(SuperUserContextView):
    def post(self, *args, **kwargs):
        ids = self.request.POST.getlist('remove')

        for pk in ids:
            wp = WordPair.objects.filter(pk=pk).first()

            if wp:
                wp.delete()

        return self.redirect_with_success('management:index', 'Removed')

class CopyWordsFromView(SuperUserContextView):
    template_name = 'app/management/form_copy_words_from.html'

    def get_context_data(self, **kwargs):
        context = super(CopyWordsFromView, self).get_context_data(**kwargs)

        dataset_id = self.kwargs['dataset_id']

        ds = DataSet.objects.filter(pk=dataset_id).first()
        datasets = sorted(
            DataSet.objects.filter(lang_pair=ds.lang_pair),
            key=lambda x: x.name_en,
        )

        if ds:
            context['dataset_id'] = dataset_id
            context['ds'] = ds
            context['datasets'] = datasets

        return context

class CopyWordsToView(SuperUserContextView):
    template_name = 'app/management/form_copy_words_to.html'

    def get_context_data(self, **kwargs):
        context = super(CopyWordsToView, self).get_context_data(**kwargs)

        target_dataset_id = self.kwargs['dataset_id']
        request = self.request

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

            context['source_ds'] = source_ds
            context['target_ds'] = target_ds
            context['words_both'] = words_both
            context['words_source_only'] = words_source_only
            context['words_target_only'] = words_target_only

        return context

    def post(self, *args, **kwargs):
        context = self.get_context_data()

        return render(self.request, self.template_name, context)

class DoCopyWords(SuperUserContextView):
    template_name = 'app/management/index.html'

    def get_context_data(self, **kwargs):
        context = super(DoCopyWords, self).get_context_data(**kwargs)

        return context

    def post(self, *args, **kwargs):
        target_dataset_id = self.kwargs['dataset_id']
        request = self.request

        target_ds = DataSet.objects.filter(id=target_dataset_id).first()

        ids = request.POST.getlist('copy')

        for pk in ids:
            wp = WordPair.objects.filter(pk=pk).first()

            if wp:
                new_link = DS2WP(
                    ds=target_ds,
                    wp=wp
                )
                new_link.save()

        return self.redirect_with_success('management:index', 'Words copied')

class SimpleDatasetsView(SuperUserContextView):
    template_name = 'app/management/simple_datasets_list.html'

    def get_context_data(self, **kwargs):
        context = super(SimpleDatasetsView, self).get_context_data(**kwargs)

        ds = SimpleDataset.objects.all()

        sets = []

        for d in ds:
            sets.append(dict(
                id=d.id,
                name=d.name,
                date=d.date,
                lines=len(d.data.split()),
            ))

        context['sets'] = sets

        return context

class SingleSimpleDatasetView(SuperUserContextView):
    template_name = 'app/management/simple_dataset.html'

    def get_context_data(self, **kwargs):
        context = super(SingleSimpleDatasetView, self).get_context_data(**kwargs)
        simple_dataset_id = self.kwargs.get('id')

        if not simple_dataset_id:
            # Creating new simple dataset
            name, data = '', ''
        else:
            d = SimpleDataset.objects.filter(pk=simple_dataset_id).first()

            if not d:
                raise Http404

            name, data = d.name, d.data

        context['name'] = name
        context['data'] = data
        context['simple_dataset_id'] = simple_dataset_id

        return context

class DoSaveSimpleDataset(SuperUserContextView):
    def post(self, *args, **kwargs):
        request = self.request
        simple_dataset_id = self.kwargs['id']

        name = request.POST['title']
        data = request.POST['data']

        d = SimpleDataset.objects.filter(pk=simple_dataset_id).first()

        if d:
            d.name = name
            d.data = data
        else:
            d = SimpleDataset(
                name=name,
                data=data,
            )

        d.save()

        return self.redirect_with_success(
            'management:view_simple_datasets',
            'Simple dataset saved',
        )

# TODO
class SimpleDatasetFromView(SuperUserContextView):
    template_name = 'app/management/form_simple_dataset_from.html'

    def get_context_data(self, **kwargs):
        context = super(SimpleDatasetFromView, self).get_context_data(**kwargs)

        dataset_id = self.kwargs['id']

        context['simple_datasets'] = SimpleDataset.objects.all()
        context['dataset_id'] = dataset_id

        return context

# TODO
class DoSaveAutoGeneratedSimpleDataset(SuperUserContextView):
    def post(self, *args, **kwargs):
        request = self.request
        dataset_id = self.kwargs['id']

        ds = DataSet.objects.filter(pk=dataset_id).first()
        simple_dataset_id = request.POST['simple_dataset_id']
        title = request.POST['title']
        base_or_target = request.POST['base_or_target']
        sds = SimpleDataset.objects.filter(pk=simple_dataset_id).first()

        if ds and sds and base_or_target in ('base', 'target') and title:
            simple_def = sds.data.split('\n')
            simple_def = [
                x.strip()
                for x in simple_def
                if x
            ]

            new_ds = DataSet(
                icon=ds.icon,
                name_base=ds.name_base,
                name_en=title,
                name_target=ds.name_target,
                lang_pair=ds.lang_pair,
                visible=False,
                word_count=0,
                pos=ds.pos,
                from_exported_file=ds.from_exported_file,
                simple_dataset=True
            )
            new_ds.save()

            wp_tmp = DS2WP.objects.filter(ds=ds)
            word_pairs = [x.wp for x in wp_tmp]

            for wp in word_pairs:
                if getattr(wp, base_or_target, None) in simple_def:
                    new_link = DS2WP(
                        ds=new_ds,
                        wp=wp
                    )
                    new_link.save()

            return self.redirect_with_success(
                'management:view_simple_datasets',
                'Simple dataset created',
            )
        else:
            return self.redirect_with_error(
                'management:view_simple_datasets',
                'Invalid input data',
            )
