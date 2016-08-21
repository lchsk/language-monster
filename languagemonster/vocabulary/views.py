# -*- coding: utf-8 -*-

import json

from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import messages
from django.http import Http404
from django.utils.translation import ugettext_lazy as _

# from models import *
from core.models import (
    LanguagePair,
    Progression,
    Language,
    DataSet,
    ErrorReport,
)

from utility.url import redirect_to_previous_page
from utility.security import create_game_session_hash
from vocabulary.impl.study import (
    get_user_games,
    get_games_played,
    # get_language_pair,
    get_datasets,
    get_user_data_sets,
    get_single_dataset,
    get_game_translations,
)
# from core.views import get_context
from utility.interface import (
    get_context,
    context,
    redirect_unauth,
    get_lang_pair_from_slugs,
    get_base_lang,
    get_progression_from_lang_pair,
)
from core.impl.user import process_games_list

from utility.views import (
    NoTemplateMixin,
    AuthContextView,
)

from core.data.base_language import BASE_LANGUAGES
from core.data.language_pair import (
    LANGUAGE_PAIRS_FLAT,
    LANGUAGE_PAIRS,
)

class AddLanguageView(AuthContextView):
    template_name = 'app/add_language.html'

    def get_context_data(self, **kwargs):
        context = super(AddLanguageView, self).get_context_data(**kwargs)

        target_languages = []
        user_lang_acronym = self._context.user.language.language.acronym

        for symbol, pair in LANGUAGE_PAIRS[user_lang_acronym].iteritems():
            if pair.visible:
                already_added = False

                for pro, lang_pair in self._context.user.studying:
                    if pro.lang_pair == symbol:
                        already_added = True
                        break

                target_languages.append(
                    dict(
                        lang=pair.target_language,
                        learning=already_added
                    )
                )

        context['languages'] = target_languages

        return context

class DoSaveLanguage(NoTemplateMixin, AuthContextView):
    def get(self, request, *args, **kwargs):
        resp = super(DoSaveLanguage, self).get(
            request,
            *args,
            **kwargs
        )

        base_slug = self._context.user.language.language.slug
        slug = self.kwargs['slug']

        lang_pair = get_lang_pair_from_slugs(
            base_slug=base_slug,
            target_slug=slug,
        )

        progression_exists = get_progression_from_lang_pair(
            self._context.user.studying,
            lang_pair
        )

        if not progression_exists:
            p = Progression(
                user=self._context.user.raw,
                lang_pair=lang_pair.symbol
            )
            p.save()

            messages.add_message(
                request,
                messages.SUCCESS,
                _('You are now learning a new language! Congratulations!')
            )

            return self.redirect('vocabulary:study', args=[slug])
        else:
            return redirect_to_previous_page(request)

class StudyView(AuthContextView):
    template_name = 'app/study.html'

    def get_context_data(self, **kwargs):
        context = super(StudyView, self).get_context_data(**kwargs)

        progressions = self._context.user.studying
        slug = kwargs['slug']

        pair_symbol = None
        pair_obj = None

        for symbol, lang_pair in LANGUAGE_PAIRS_FLAT.iteritems():
            if (
                lang_pair.target_language.slug == slug and
                lang_pair.base_language.acronym == self._context.user.language.language.acronym
            ):
                pair_symbol = symbol
                pair_obj = lang_pair
                break

        if pair_symbol is not None:
            ds = get_datasets(pair_symbol)
            basic_ds = [d for d in ds if d.simple_dataset]
            user_data_sets = get_user_data_sets(self._context.user.raw)

            context['pair'] = pair_obj
            context['datasets'] = ds
            context['basic_datasets'] = basic_ds
            context['user_data_sets'] = user_data_sets

            return context
        else:
            raise Http404


# @login_required
@context
@redirect_unauth
def play(request, target_slug, dataset_slug, ctx):
    """Game screen"""

    # base_slug = c['user'].current_language.slug

    pair = None
    symbol = None
    user_lang_acronym = ctx['basic']['user_lang'].language.acronym

    for lang_symbol, lang_pair in LANGUAGE_PAIRS_FLAT.iteritems():
        if (
            lang_pair.target_language.slug == target_slug and
            lang_pair.base_language.acronym == user_lang_acronym
        ):
            pair = lang_pair
            symbol = lang_symbol
            break

    d = get_single_dataset(
        symbol,
        dataset_slug
    )

    if not d:
        return HttpResponseRedirect(reverse('index'))

    game_session_id = create_game_session_hash(
        ctx['user'],
        d
    )

    ctx['game'] = True
    ctx['dataset'] = d
    ctx['pair'] = pair

    ctx['data'] = {
        'dataset_id': str(d.id),
        'email': str(ctx['user'].user.email),
        'game_session_id': game_session_id
    }

    user_games = get_user_games(ctx['user'])

    ctx['translations'] = get_game_translations()
    ctx['games'] = process_games_list(
        monster_user=ctx['user'],
        games=settings.GAMES,
        user_games=user_games
    )
    ctx['games_played']  = [
        user_game['game']
        for user_game in user_games
        if user_game['played']
    ]
    # c['games_played'] = get_games_played(monster_user=c['user'])
    ctx['canvas_only'] = settings.GAMES_USE_CANVAS_ONLY

    if ctx:
        return render(request, 'app/game.html', ctx)

    return redirect_to_previous_page(request)


# TODO: only accept localhost
# @login_required
@context
@redirect_unauth
def report_error(request, ctx):
    d = request.POST.get('json')

    if d:
        data = json.loads(d)

        username = data.get('username', None)
        dataset_id = data.get('dataset_id', None)
        text = data.get('text', None)

        if not username and dataset_id and text:
            report = ErrorReport(
                user=ctx['user'],
                text=text,
                data_set=DataSet.objects.filter(id=dataset_id).first()
            )
            report.save()

    return HttpResponseRedirect(reverse('index'))
