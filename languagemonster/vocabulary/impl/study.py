# -*- coding: utf-8 -*-

import random
import json

from django.utils.translation import ugettext_lazy as _

from core.models import (
    DataSet,
    DataSetProgress,
    DS2WP,
    UserResult,
    Progression,
    MonsterUserGame,
    UserWordPair,
)
import ctasks.game_tasks as game_tasks

def get_user_games(monster_user):
    return [{
            'game': mu_game.game,
            'played': mu_game.played,
            'banned': mu_game.banned
        }
        for mu_game in MonsterUserGame.objects.filter(
            monster_user=monster_user
        )
    ]

def get_datasets(language_pair):
    return DataSet.objects.filter(
        lang_pair=language_pair,
        visible=True,
        status='A',
    ).order_by('-learners')

def get_single_dataset(lang_pair_symbol, dataset_slug):
    return DataSet.objects.filter(
        slug=dataset_slug,
        lang_pair=lang_pair_symbol,
        status='A',
    ).first()

def get_user_data_sets(user):
    sets = []
    progress = DataSetProgress.objects.filter(user=user)

    for p in progress:
        sets.append(p.data_set)

    return sets

def get_words_to_repeat(monster_user, words):
    to_repeat = UserWordPair.objects.filter(
        user=monster_user,
        repeat=True,
    ).select_related('word_pair')

    return [
        word_pair
        for word_pair in to_repeat
        if word_pair in words
    ]

def get_game_words(
    dataset_id,
    monster_user,
    rounds=10,
    include_words_to_repeat=True,
    nsets=1,
):
    word_pairs = [
        wp.wp
        for wp in DS2WP.objects.filter(
            ds_id=dataset_id
        ).select_related('wp')
    ]

    if len(word_pairs) < 4 or len(word_pairs) < rounds:
        raise RuntimeError(
            'There must be at least 4 word pairs, instead: {}, '
            'dataset_id: {}'.format(len(word_pairs), dataset_id)
        )

    if include_words_to_repeat:
        to_repeat = get_words_to_repeat(
            monster_user=monster_user,
            words=word_pairs,
        )
    else:
        to_repeat = []

    returned_words = []

    returned_words.extend(to_repeat)

    items_to_return = nsets * rounds
    items_to_pick = items_to_return - len(returned_words)

    sentinel = 0;

    while True or sentinel < 1000:
        sentinel += 1

        if sentinel == 1000:
            raise RuntimeError('Too many iterations')

        random.shuffle(word_pairs)
        returned_words.extend(word_pairs)

        words_cnt = len(returned_words)

        rounded_size = words_cnt - words_cnt % rounds

        returned_words = returned_words[:rounded_size]

        if len(returned_words) >= items_to_return:
            break

    resp = []

    for nset in xrange(nsets):
        resp.append(dict(
            to_ask=[
                dict(
                    id=word_pair.id,
                    words=[
                        word_pair.base,
                        word_pair.target,
                    ]
                )
                for word_pair in returned_words[
                    nset * rounds:nset * rounds + rounds
                ]
            ]
        ))

    return resp

def mark_wordpair(words, options):
    for wordpair_id in words:
        # TODO
        UserWordPair.objects.filter(word_pair__id=wordpair_id).update(
            **options
        )

def get_game_translations():

    d = {}
    d['Good'] = unicode(_(u'Good'))
    d['Wrong'] = unicode(_(u'Wrong'))
    d['Well done'] = unicode(_(u'Well done'))
    d['Continue'] = unicode(_(u'Continue'))

    d['Error when sending results'] = unicode(_(u'Error when sending results'))
    d['Results were sent'] = unicode(_(u'Results were sent'))
    d['Sending results...'] = unicode(_(u'Sending results...'))
    d['Sending results...'] = unicode(_(u'Sending results...'))
    d['Language Monster'] = unicode(_(u'Language Monster'))
    d['Loading, please wait'] = unicode(_(u'Loading, please wait'))
    d['Server error, please try again'] = unicode(_(u'Server error, please try again'))
    d['Try again'] = unicode(_(u'Try again'))

    return json.dumps(d)


def do_save_results(
    dataset_id,
    monster_user,
    game,
    mark,
    words_learned,
    to_repeat
):
    """Save results in database.

    Used by API and JS.
    """

    # Check if we need to increment learners variable
    # Don't move this part: it needs to be before saving
    # a UserResult object

    dataset = DataSet.objects.filter(id=dataset_id)

    if len(dataset) != 1:
        raise Exception("NOPE")

    dataset = dataset[0]

    user_games = MonsterUserGame.objects.filter(
        monster_user=monster_user,
        game=game,
        played=True,
    )

    if not user_games:
        monster_user_game = MonsterUserGame(
            monster_user=monster_user,
            game=game,
            played=True,
        )

        monster_user_game.save()

    users_results_cnt = UserResult.objects.filter(
        user=monster_user,
        data_set=dataset,
    ).count()

    if users_results_cnt == 0:
        # User has not been learning this dataset so far

        progressions = Progression.objects.filter(
            user=monster_user,
            lang_pair=dataset.lang_pair,
        )

        if len(progressions) != 1:
            raise Exception("111")

        # Increase number of datasets user is learning
        monster_user.datasets += 1
        monster_user.save()

        # Increase number of datasets the user is learning in this language
        progressions[0].datasets += 1
        progressions[0].save()

        # Increase number of people learning this dataset
        dataset.learners += 1
        dataset.save()

    result = UserResult(
        user=monster_user,
        game=game,
        data_set=dataset,
        mark=mark,
    )

    result.save()

    mark_wordpair(words_learned, dict(
        learned=True,
        repeat=False,
    ))

    mark_wordpair(to_repeat, dict(
        learned=False,
        repeat=True,
    ))

    # Update stats
    game_tasks.update_user_stats.delay(monster_user.user.email, dataset.id)
