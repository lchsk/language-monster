from datetime import (
    datetime,
    timedelta,
)

from mock import (
    Mock,
    MagicMock,
    patch,
)

from ctasks.game_tasks import (
    count_user_words,
    update_streak,
    compute_strength,
)

from utility import mock_objects as mo

streak_tests = [
    dict(
        ret=[],
        results=[0, 0, 0],
    ),
    dict(
        ret=[
            Mock(
                user=mo.USER_1,
                data_set=mo.DATASET_1,
                mark=50,
                date=datetime.today(),
            ),
        ],
        results=[1, 50, 1],
    ),
    dict(
        ret=[
            Mock(
                user=mo.USER_1,
                data_set=mo.DATASET_1,
                mark=60,
                date=datetime.today()
            ),
            Mock(
                user=mo.USER_1,
                data_set=mo.DATASET_1,
                mark=40,
                date=datetime.today() - timedelta(days=1)
            ),
            Mock(
                user=mo.USER_1,
                data_set=mo.DATASET_1,
                mark=80,
                date=datetime.today() - timedelta(days=2)
            ),
        ],
        results=[3, 60, 3],
    ),
    dict(
        ret=[
            Mock(
                user=mo.USER_1,
                data_set=mo.DATASET_1,
                mark=60,
                date=datetime.today() - timedelta(days=3)
            ),
            Mock(
                user=mo.USER_1,
                data_set=mo.DATASET_1,
                mark=80,
                date=datetime.today() - timedelta(days=4)
            ),
        ],
        results=[0, 70, 2],
    ),
    dict(
        ret=[
            Mock(
                user=mo.USER_1,
                data_set=mo.DATASET_1,
                mark=10,
                date=datetime.today()
            ),
            Mock(
                user=mo.USER_1,
                data_set=mo.DATASET_1,
                mark=60,
                date=datetime.today() - timedelta(days=3)
            ),
            Mock(
                user=mo.USER_1,
                data_set=mo.DATASET_1,
                mark=80,
                date=datetime.today() - timedelta(days=4)
            ),
        ],
        results=[1, 50, 3],
    )
]

@patch('core.models.UserWordPair.objects.filter')
@patch('core.models.DS2WP.objects.filter')
def test_count_words_user_learned(mock_ds2wp, mock_userwordpair):
    cnt = count_user_words(mo.USER_1, mo.PROGRESSION_1)

    assert cnt == 0

    mock_userwordpair.return_value = [
        Mock(user=mo.USER_1, word_pair=mo.WP_10, learned=True),
        Mock(user=mo.USER_1, word_pair=mo.WP_11, learned=True),
    ]

    mock_userwordpair.assert_called_once_with(learned=True, user=mo.USER_1)

    mock_ds2wp.return_value = mo.LINKS_1

    cnt = count_user_words(mo.USER_1, mo.PROGRESSION_1)

    assert cnt == 2

@patch('core.models.UserResult.objects.filter')
def test_compute_user_streak(mock_userresult):
    for test in streak_tests:
        mock_userresult.return_value = MagicMock()
        mock_userresult.return_value.order_by.return_value = test['ret']

        streak, avg, cnt = update_streak(mo.USER_1, mo.PROGRESSION_1)

        mock_userresult.assert_called_with(user=mo.USER_1)

        exp_streak, exp_avg, exp_cnt = test['results']

        assert streak == exp_streak
        assert avg == exp_avg
        assert cnt == exp_cnt

def test_compute_strength():
    trend, new_strength = compute_strength(
        current_strength=0,
        words=0,
        streak=0,
        average=0,
        levels=0
    )

    assert trend == 0
    assert new_strength == 0

    trend, new_strength = compute_strength(
        current_strength=10,
        words=50, #5
        streak=0, # 0
        average=80, # 3
        levels=5 # 2
    )

    assert trend == 0
    assert new_strength == 10

    trend, new_strength = compute_strength(
        current_strength=50,
        words=250, #25
        streak=5, # 1
        average=75, # 3
        levels=50 # 15
    )

    assert trend == -1
    assert new_strength == 44

    trend, new_strength = compute_strength(
        current_strength=80,
        words=750, #75
        streak=8, # 2
        average=80, # 3
        levels=120 # 36
    )

    assert trend == 1
    assert new_strength == 116
