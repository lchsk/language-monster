from __future__ import absolute_import
import logging

from django.conf import settings

from datetime import (
    date,
    timedelta,
)

from celery import shared_task
from celery.utils.log import get_task_logger

from core.models import (
    UserWordPair,
    UserResult,
    DataSet,
    MonsterUser,
    Progression,
    DS2WP,
)

logger = logging.getLogger(__name__)
settings.LOGGER(logger, settings.LOG_WORKERS_HANDLER)


def count_user_words(user, progression):
    '''
        Counts how many words a user knows in a single language.
    '''

    logger.info('Count words: %s', progression)

    user_words = [
        uwp.word_pair
        for uwp in UserWordPair.objects.filter(
            user=user,
            learned=True
        )
    ]

    count = 0

    all_words = [
        link.wp
        for link in DS2WP.objects.filter(
            ds__pair=progression.pair
        )
    ]

    for uw in user_words:
        if uw in all_words:
            count += 1

    logger.info(
        'user_words: %s, all_words: %s, count: %s',
        len(user_words),
        len(all_words),
        count
    )

    progression.words = count
    progression.save()

    return count


def update_streak(user, progression):
    '''
        Updates user streak (number of straight days with a level finished)
        and average.
    '''

    results = UserResult.objects.filter(user=user).order_by('-date')
    streak = 0
    marks = 0
    results_count = 0
    date_tmp = date.today()

    for r in results:
        if r and progression and r.data_set.pair == progression.pair:
            marks += r.mark
            results_count += 1

            if (
                date_tmp.day == r.date.day and
                date_tmp.month == r.date.month and
                date_tmp.year == r.date.year
            ):
                streak += 1
                date_tmp -= timedelta(days=1)

    progression.streak = streak

    if results_count > 0:
        progression.average = int(round(marks / float(results_count)))
    else:
        progression.average = 0

    progression.save()

    return streak, progression.average, results_count


def compute_strength(current_strength, words, streak, average, levels):
    new_stength = round(
        words * 0.1 + streak * 0.2 + levels * 0.3 + (average * 0.1) * 0.4
    )

    trend = 0

    if new_stength > current_strength:
        trend = 1
    elif new_stength < current_strength:
        trend = -1

    return trend, new_stength


@shared_task
def update_user_stats(email, dataset_id):
    '''
        Celery task called after finishing a single level in a game.
        Updates user statistics for a single language.
    '''

    d = DataSet.objects.filter(id=int(dataset_id)).first()
    u = MonsterUser.objects.filter(user__email=email).first()

    if not d:
        logger.critical('Dataset %s not found', dataset_id)

    if not u:
        logger.critical('User %s not found', email)

    language = Progression.objects.filter(
        user=u,
        pair=d.pair
    ).first()

    if u and d and language:
        words = count_user_words(u, language)
        streak, average, levels = update_streak(u, language)

        logger.info('Updating stats of a single user ({0})'.format(email))

        language.strength, language.trend = compute_strength(
            language.strength,
            words,
            streak,
            average,
            levels
        )
        language.save()

@shared_task
def update_all_users_stats():
    '''
        Celery task run daily (during the night) to update stats of all users.
        It might be heavy.
    '''

    logger.info("Started procedure to update statistics of all users.")

    users = MonsterUser.objects.all()

    for u in users:

        user_langs = Progression.objects.filter(user=u)

        for language in user_langs:

            words = count_user_words(u, language)
            streak, average, levels = update_streak(u, language)

            language.strength, language.trend = compute_strength(
                language.strength,
                words,
                streak,
                average,
                levels
            )

            language.save()

    logger.info("Finished procedure to update statistics for all users.")
