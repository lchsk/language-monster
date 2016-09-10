# -*- encoding: utf-8 -*-

from mock import (
    Mock,
    patch,
)

from vocabulary.impl.study import get_words_to_repeat

@patch('core.models.UserWordPair.objects.filter')
def test_get_words_to_repeat(m_wp):
    data = [
        Mock(word_pair=Mock(id=1, base=u'kot', target=u'cat')),
        Mock(word_pair=Mock(id=2, base=u'pies', target=u'dog')),
        Mock(word_pair=Mock(id=3, base=u'caballo', target=u'horse')),
    ]

    m_wp.return_value.select_related.return_value = data

    to_repeat = get_words_to_repeat(
        monster_user=None,
        words=data[:2] + [
            Mock(word_pair=Mock(id=4, base=u'ptak', target=u'bird')),
            Mock(word_pair=Mock(id=5, base=u'ryba', target=u'fish')),
        ]
    )

    assert len(to_repeat) == 2
    assert data[0] in to_repeat
    assert data[1] in to_repeat
    assert data[2] not in to_repeat
