# -*- encoding: utf-8 -*-

from mock import (
    Mock,
    patch,
)

from vocabulary.impl.study import get_game_words

@patch('core.models.DS2WP.objects.filter')
def test_get_words_one_set_without_repeated(m_ds2wp):
    nsets = 1
    rounds = 5
    repeated = False
    data = [
        Mock(wp=Mock(id=1, base=u'kot', target=u'cat')),
        Mock(wp=Mock(id=2, base=u'pies', target=u'dog')),
        Mock(wp=Mock(id=3, base=u'koń', target=u'horse')),
    ]

    m_ds2wp.return_value.select_related.return_value = data

    resp = get_game_words(
        dataset_id=None,
        monster_user=None,
        rounds=rounds,
        include_words_to_repeat=repeated,
        nsets=nsets,
    )

    _assert_resp_no_repeated(resp, nsets, rounds, _transform_data(data))


@patch('core.models.DS2WP.objects.filter')
def test_get_words_multiple_sets_without_repeated(m_ds2wp):
    nsets = 3
    rounds = 4
    repeated = False
    data = [
        Mock(wp=Mock(id=1, base=u'kot', target=u'cat')),
        Mock(wp=Mock(id=2, base=u'pies', target=u'dog')),
        Mock(wp=Mock(id=3, base=u'koń', target=u'horse')),
    ]

    m_ds2wp.return_value.select_related.return_value = data

    resp = get_game_words(
        dataset_id=None,
        monster_user=None,
        rounds=rounds,
        include_words_to_repeat=repeated,
        nsets=nsets,
    )

    _assert_resp_no_repeated(resp, nsets, rounds, _transform_data(data))

@patch('core.models.DS2WP.objects.filter')
@patch('vocabulary.impl.study.get_words_to_repeat')
def test_get_words_with_repeated(m_repeat, m_ds2wp):
    nsets = 2
    rounds = 2
    repeated = True
    data = [
        Mock(wp=Mock(id=4, base=u'kot', target=u'cat')),
        Mock(wp=Mock(id=5, base=u'pies', target=u'dog')),
        Mock(wp=Mock(id=6, base=u'koń', target=u'horse')),
    ]

    m_repeat.return_value = [
        Mock(id=3, base=u'kot', target=u'cat'),
        Mock(id=2, base=u'pies', target=u'dog'),
    ]
    m_ds2wp.return_value.select_related.return_value = data

    resp = get_game_words(
        dataset_id=None,
        monster_user=None,
        rounds=rounds,
        include_words_to_repeat=repeated,
        nsets=nsets,
    )

    assert len(resp) == nsets

    for word_set in resp:
        assert len(word_set['to_ask']) == rounds

    assert resp[0]['to_ask'][0]['id'] == 3
    assert resp[0]['to_ask'][1]['id'] == 2

def _transform_data(data):
    return {
        word_pair.wp.id: word_pair.wp
        for word_pair in data
    }

def _assert_resp_no_repeated(resp, nsets, rounds, transformed):
    assert len(resp) == nsets

    for word_set in resp:
        assert len(word_set['to_ask']) == rounds

        for word_pair in word_set['to_ask']:
            assert word_pair['id'] in transformed.keys()
            assert word_pair['words'][0] == transformed[word_pair['id']].base
            assert word_pair['words'][1] == transformed[word_pair['id']].target
