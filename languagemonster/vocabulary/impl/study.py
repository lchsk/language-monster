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


def get_games_played(monster_user):
    return [
        monster_user_game.game
        for monster_user_game in MonsterUserGame.objects.filter(
            monster_user=monster_user,
            played=True
        )
    ]


def get_language_pair(base_language, target_slug):
    """TODO: check if it can be removed"""

    # base_language = Language.objects.filter(slug=base_slug).first()
    target_language = Language.objects.filter(slug=target_slug).first()

    if base_language and target_language:
        return LanguagePair.objects.filter(
            base_language=base_language,
            target_language=target_language
        ).first()
    else:
        return False


def get_datasets(language_pair):
    return DataSet.objects.filter(
        lang_pair=language_pair,
        visible=True,
        status='A',
    ).order_by('-learners')


def get_user_progress(user):
    return DataSetProgress.objects.filter(user=user)


def get_user_data_sets(user):
    sets = []
    progress = DataSetProgress.objects.filter(user=user)

    for p in progress:
        sets.append(p.data_set)

    return sets


def get_single_dataset(lang_pair_symbol, dataset_slug):

    # ds = DataSet.objects.filter(
    #     slug=dataset_slug
    # ).prefetch_related('pair', 'pair__base_language', 'pair__target_language')

    return DataSet.objects.filter(
        slug=dataset_slug,
        lang_pair=lang_pair_symbol,
        status='A',
        # pair__base_language=base_language,
        # pair__target_language__slug=target_slug
    ).first()

    # if ds:
    #     for d in ds:
    #         if (
    #             d.pair.base_language == base_language and
    #             d.pair.target_language.slug == target_slug
    #         ):
    #             return d
    # 
    # return False


def get_dataset_content_db(dataset_id):
    """
        Returns all Word Pairs from a data set.

        Args:
            dataset_id(int): ID of a dataset.

        Returns:
            [WordPair]
    """

    word_pairs = DS2WP.objects.filter(ds_id=dataset_id).select_related('wp')

    return [
        wp.wp
        for wp in word_pairs
    ]


def get_words_to_repeat(user, words):
    """
        Returns a list of word pairs a user should repeat.

        Args:
            user(MonsterUser): A user.

            words([WordPair]): A list of word pairs from a data set.

        Returns:
            [WordPair]: A list of word pairs to repeat.
    """

    # TODO: this function into a single query

    user_word_pairs = [
        user_word_pair.word_pair
        for user_word_pair in UserWordPair.objects.filter(
            user=user,
            repeat=True,
        )
    ]

    return [
        wp
        for wp in user_word_pairs
        if wp in words
    ]

    # return [
    #     user_word_pair.word_pair
    #     for user_word_pair in UserWordPair.objects.filter(
    #         user=user,
    #         repeat=True
    #     )
    # ]


def convert_to_string_array(words):
    """
        Converts a list of Word Pairs from DB model to a representation
        suitable for consumption.

        E.g.:
            Input: [WordPair, WordPair, WordPair]
            Output: [
                [cat, gato],
                [dog, perro],
                [fish, pez]
            ]

        Args:
            words([WordPair]): A list of Word Pairs.

        Returns:
            [[str, str]]: An array of arrays consisting of two elements.
    """

    return [
        [wp.base, wp.target]
        for wp in words
    ]

    # arr = []
    # 
    # for wp in words:
    #     arr.append([wp.base, wp.target])
    # 
    # return arr

def get_single_game_data_array(words, max_rounds, to_repeat=[]):
    """
        Returns a single array with random/repeated words.

        Args:
            words([WordPair]): A list of Word Pairs.

            max_rounds(int): Maximum number of word pairs in a single array.

            to_repeat([WordPair]): A list of Word Pairs to repeat.
    """

    to_ask = []

    if to_repeat:
        to_ask += list(set(to_repeat))

    while len(to_ask) < max_rounds:
        random_wp = random.choice(words)

        if random_wp not in to_ask:
            to_ask.append(random_wp)

    random.shuffle(to_ask)

    return convert_to_string_array(to_ask)

# import sys
# from profiling import profile
# import logging
# l = logging.getLogger('django.db.backends')
# l.setLevel(logging.DEBUG)
# l.addHandler(logging.StreamHandler())

# @profile(
# stats=True, stats_buffer=sys.stdout
# )
def game_data(
    dataset_id,
    user,
    max_rounds,
    to_json=True,
    include_words_to_repeat=True,
    number_of_sets=1
):
    """
        Returns either a single array or *number_of_sets* arrays with vocabulary.

        Args:
            dataset_id(int): ID of dataset to select vocabulary from.

            user(MonsterUser): User for whom words are prepared.

            max_rounds(int): Maximum number of word pairs in a single array.

            to_json(boolean): If true, results will be converted to a JSON.

            include_words_to_repeat(boolean): If true, word pairs that a user
                got wrong will be included. If *number_of_sets* is greater
                than 1, words to repeat will only be included in first array.

            number_of_sets(int): Number of arrays to return.

        Returns:
            (single array):
                {
                    "to_ask": [
                        ["dog", "pies"],
                        ["cat", "kot"]
                    ]
                }

            (two arrays):
                [
                    {
                        "to_ask": [
                            ["dog", "pies"],
                            ["cat", "kot"]
                        ]
                    },
                    {
                        "to_ask": [
                            ["fish", "ryba"],
                            ["parrot", "papuga"]
                        ]
                    }
                ]
    """

    # pair = dataset.pair

    # That is probably not needed
    # already_added = Progression.objects.filter(
    #     user=user,
    #     pair=pair
    # ).first()

    words = get_dataset_content_db(dataset_id)
    random.shuffle(words)

    if include_words_to_repeat:
        to_repeat = get_words_to_repeat(
            user=user,
            words=words
        )
    else:
        to_repeat = []

    if number_of_sets == 1:
        data = dict(
            to_ask=get_single_game_data_array(
                words=words,
                max_rounds=max_rounds,
                to_repeat=to_repeat
            )
        )
    else:
        data = []

        for i in xrange(number_of_sets):
            data.append(
                dict(
                    to_ask=get_single_game_data_array(
                        words=words,
                        max_rounds=max_rounds,
                        to_repeat=to_repeat if i == 0 else []
                    )
                )
            )

    if to_json:
        return json.dumps(data)
    else:
        return data


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
