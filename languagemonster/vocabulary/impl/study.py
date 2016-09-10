# -*- coding: utf-8 -*-

import random
import json

from django.utils.translation import ugettext_lazy as _

from core.models import (
    Language,
    LanguagePair,
    DataSet,
    DataSetProgress,
    DS2WP,
    UserResult,
    Progression,
    MonsterUserGame,
    UserWordPair,
)
import ctasks.game_tasks as game_tasks

# REMOVE?
def get_user_games(monster_user):
    return [
        {
            'game': mu_game.game,
            'played': mu_game.played,
            'banned': mu_game.banned
        }
        for mu_game in MonsterUserGame.objects.filter(
            monster_user=monster_user
        )
    ]


# REMOVE?
def get_games_played(monster_user):
    return [
        monster_user_game.game
        for monster_user_game in MonsterUserGame.objects.filter(
            monster_user=monster_user,
            played=True
        )
    ]

#"""TODO: check if it can be removed"""
def get_language_pair(base_language, target_slug):
    # base_language = Language.objects.filter(slug=base_slug).first()
    target_language = Language.objects.filter(slug=target_slug).first()

    if base_language and target_language:
        return LanguagePair.objects.filter(
            base_language=base_language,
            target_language=target_language
        ).first()
    else:
        return False


# CHECK IF USED
def get_datasets(language_pair):
    return DataSet.objects.filter(
        lang_pair=language_pair,
        visible=True,
        status='A',
    ).order_by('-learners')


# CHECK IF USED
def get_user_progress(user):
    return DataSetProgress.objects.filter(user=user)


# CHECK IF USED
def get_user_data_sets(user):
    sets = []
    progress = DataSetProgress.objects.filter(user=user)

    for p in progress:
        sets.append(p.data_set)

    return sets


# CHECK IF USED
def get_single_dataset(lang_pair_symbol, dataset_slug):
    return DataSet.objects.filter(
        slug=dataset_slug,
        lang_pair=lang_pair_symbol,
        status='A',
    ).first()

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

    if include_words_to_repeat:
        to_repeat = get_words_to_repeat(
            monster_user=monster_user,
            words=word_pairs,
        )
    else:
        to_repeat = []

    returned_words = []

    returned_words.extend(to_repeat)

    items_to_pick = nsets * rounds - len(returned_words)

    for _ in xrange(items_to_pick):
        returned_words.append(random.choice(word_pairs))

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

def mark_wordpair(d, user, words, options):

    wp_tmp = DS2WP.objects.filter(ds=d)
    pairs = [i.wp for i in wp_tmp]

    for wp in words:
        for pair in pairs:
            if wp[0] == pair.base and wp[1] == pair.target:
                user_pair = UserWordPair.objects.filter(
                    user=user,
                    word_pair=pair
                ).first()

                if not user_pair:
                    user_pair = UserWordPair(
                        user=user,
                        word_pair=pair
                    )

                if options:
                    for k, v in options.iteritems():
                        setattr(user_pair, k, v)

                user_pair.save()


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
    dataset,
    email,
    user,
    game,
    mark,
    words_learned,
    to_repeat
):
    """
        Actually saves results from a game.
        Called from API and JS API calls.
    """

    # Check if we need to increment learners variable
    # Don't move this part: it needs to be before saving
    # a UserResult object

    if MonsterUserGame.objects.filter(
        monster_user=user,
        game=game,
        played=True
    ).first() is None:
        monster_user_game = MonsterUserGame(
            monster_user=user,
            game=game,
            played=True
        )
        monster_user_game.save()

    c = UserResult.objects.filter(
        user=user,
        data_set=dataset
    ).count()

    if c == 0:
        p = Progression.objects.filter(
            user=user,
            lang_pair=dataset.lang_pair
        ).first()

        # Number of datasets user is learning up

        user.datasets += 1
        user.save()

        if p:
            p.datasets += 1
            p.save()

        # Number of learners for the dataset up
        dataset.learners += 1
        dataset.save()

    # Save UserResult

    result = UserResult(
        user=user,
        game=game,
        data_set=dataset,
        mark=mark,
    )
    result.save()

    # Update WordPairs
    mark_wordpair(dataset, user, words_learned, {
        'learned': True,
        'repeat': False
    })
    mark_wordpair(dataset, user, to_repeat, {'learned': False, 'repeat': True})

    # Update user's stats

    game_tasks.update_user_stats.delay(email, dataset_id)
