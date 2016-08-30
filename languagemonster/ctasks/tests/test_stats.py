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

@patch('core.models.UserWordPair.objects.filter')
@patch('core.models.DS2WP.objects.filter')
def test_count_words_user_learned(mock_ds2wp, mock_userwordpair):
    user = Mock()

    lang1 = Mock()
    lang2 = Mock()

    lp = Mock(
        base_language=lang1,
        target_language=lang2,
    )

    progression1 = Mock(
        user=user,
        pair=lp,
    )

    cnt = count_user_words(user, progression1)

    assert cnt == 0

    wp1 = Mock(base='dog', target='pies')
    wp2 = Mock(base='cat', target='kot')
    wp3 = Mock(base='lion', target='lew')
    wp4 = Mock(base='pear', target='gruszka')

    words = [wp1, wp2, wp3]

    ds = Mock(pair=lp)

    link1 = Mock(ds=ds, wp=wp1)
    link2 = Mock(ds=ds, wp=wp2)
    link3 = Mock(ds=ds, wp=wp3)
    link4 = Mock(ds=ds, wp=wp4)

    mock_userwordpair.return_value = [
        Mock(user=user, word_pair=wp1, learned=True),
        Mock(user=user, word_pair=wp2, learned=True),
    ]

    mock_userwordpair.assert_called_with(learned=True, user=user)

    mock_ds2wp.return_value = [link1, link2, link3, link4]

    cnt = count_user_words(user, progression1)

    assert cnt == 2

@patch('core.models.UserResult.objects.filter')
def test_compute_user_streak(mock_userresult):
    user = Mock()

    lang1 = Mock()
    lang2 = Mock()

    lp = Mock(
        base_language=lang1,
        target_language=lang2,
    )

    progression1 = Mock(
        user=user,
        pair=lp,
    )

    # First case - no results

    mock_userresult.return_value = MagicMock()
    mock_userresult.return_value.order_by.return_value = []

    streak, avg, cnt = update_streak(user, progression1)

    mock_userresult.assert_called_with(user=user)

    assert cnt == 0
    assert streak == 0
    assert avg == 0


    # Second case - a single result
    from datetime import datetime, timedelta

    mock_userresult.return_value = MagicMock()
    mock_userresult.return_value.order_by.return_value = [
        Mock(
            user=user,
            data_set=Mock(pair=lp),
            mark=50,
            date=datetime.today()
        )
    ]

    streak, avg, cnt = update_streak(user, progression1)

    assert cnt == 1
    assert streak == 1
    assert avg == 50

    # # Third case - several cases

    mock_userresult.return_value = MagicMock()
    mock_userresult.return_value.order_by.return_value = [
        Mock(
            user=user,
            data_set=Mock(pair=lp),
            mark=60,
            date=datetime.today()
        ),
        Mock(
            user=user,
            data_set=Mock(pair=lp),
            mark=40,
            date=datetime.today() - timedelta(days=1)
        ),
        Mock(
            user=user,
            data_set=Mock(pair=lp),
            mark=80,
            date=datetime.today() - timedelta(days=2)
        )
    ]

    streak, avg, cnt = update_streak(user, progression1)

    assert cnt == 3
    assert streak == 3
    assert avg == 60

    # 4th case - several cases

    mock_userresult.return_value = MagicMock()
    mock_userresult.return_value.order_by.return_value = [
        Mock(
            user=user,
            data_set=Mock(pair=lp),
            mark=60,
            date=datetime.today() - timedelta(days=3)
        ),
        Mock(
            user=user,
            data_set=Mock(pair=lp),
            mark=80,
            date=datetime.today() - timedelta(days=4)
        ),
    ]

    streak, avg, cnt = update_streak(user, progression1)

    assert cnt == 2
    assert streak == 0
    assert avg == 70

    # 5th case - several cases

    mock_userresult.return_value = MagicMock()
    mock_userresult.return_value.order_by.return_value = [
        Mock(
            user=user,
            data_set=Mock(pair=lp),
            mark=10,
            date=datetime.today()
        ),
        Mock(
            user=user,
            data_set=Mock(pair=lp),
            mark=60,
            date=datetime.today() - timedelta(days=3)
        ),
        Mock(
            user=user,
            data_set=Mock(pair=lp),
            mark=80,
            date=datetime.today() - timedelta(days=4)
        ),
    ]

    streak, avg, cnt = update_streak(user, progression1)

    assert cnt == 3
    assert streak == 1
    assert avg == 50

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
