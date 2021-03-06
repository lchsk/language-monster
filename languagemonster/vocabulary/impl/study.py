# -*- coding: utf-8 -*-

import random
import json
import logging

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

from utility.exception import NoDataFound

logger = logging.getLogger(__name__)

# Minimum number of words in a set
MIN_WORDS = 4

# Maximum number of iterations during set generation
MAX_ITERATIONS = 50

class TooManyWordsRequested(Exception):
    pass

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

def get_datasets_by_base(base_language):
    """Load sets for a given base language."""

    return DataSet.objects.filter(
        lang_pair__contains=base_language + '_',
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
        if wp.wp.visible
    ]

    if len(word_pairs) < max(MIN_WORDS, rounds):
        raise TooManyWordsRequested(
            '{} words were requested, {} available, '
            'dataset_id: {}'.format(rounds, len(word_pairs), dataset_id)
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
    set_no = 0

    while True:
        set_no += 1

        if set_no > MAX_ITERATIONS:
            logger.warning('Too many iterations: %s', set_no)

            raise RuntimeError('Too many iterations: %s', set_no)

        random.shuffle(word_pairs)
        returned_words.extend(word_pairs)

        words_cnt = len(returned_words)

        rounded_size = words_cnt - words_cnt % rounds

        returned_words = returned_words[:rounded_size]

        for n, m in zip(
            xrange(0, len(returned_words), rounds),
            xrange(rounds, len(returned_words) + rounds, rounds),
        ):
            # Ensure there are no repeated base/target values
            bases = len(set(word.base for word in returned_words[n:m]))
            targets = len(set(word.target for word in returned_words[n:m]))

            if bases != targets:
                logger.warning(
                    'Number of bases different than number of targets: %s, %s. '
                    'Skipping to next iteration',
                    bases,
                    targets,
                )

                # Reset
                returned_words = []

                continue

        if len(returned_words) >= items_to_return:
            break

    logger.info(
        'Requested %s sets generated after %s iterations. set: %s, rounds: %s',
        nsets,
        set_no,
        dataset_id,
        rounds,
    )

    if set_no > nsets:
        logger.warning(
            'It took more than expected no. of iterations %s > %s, set: %s, words: %s',
            set_no,
            nsets,
            dataset_id,
            returned_words,
        )

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

def mark_wordpair(monster_user, words, options):
    for wordpair_id in words:
        try:
            user_word_pair = UserWordPair.objects.get(
                word_pair__id=wordpair_id,
                user=monster_user,
            )

            user_word_pair.repeat = options['repeat']
            user_word_pair.learned = options['learned']

            created = False

        except UserWordPair.DoesNotExist:
            user_word_pair = UserWordPair(
                word_pair_id=wordpair_id,
                user=monster_user,
                repeat=options['repeat'],
                learned=options['learned'],
            )

            created = True

        logger.info(
            'UserWordPair {}, created: {}, wordpair_id: {}, '
            'user: {}, options: {}'.format(
                user_word_pair.id,
                created,
                wordpair_id,
                monster_user,
                options,
            )
        )

        user_word_pair.save()

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
        logger.warning('Dataset not found, id:' % dataset_id)

        raise NoDataFound()

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
            logger.warning('Progression not found, user: {}, pair: {}'.format(
                monster_user,
                dataset.lang_pair,
            ))

            raise NoDataFound()

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

    mark_wordpair(monster_user, words_learned, dict(
        learned=True,
        repeat=False,
    ))

    mark_wordpair(monster_user, to_repeat, dict(
        learned=False,
        repeat=True,
    ))

    # Update stats
    game_tasks.update_user_stats.delay(monster_user.user.email, dataset.id)
