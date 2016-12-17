#! -*- encoding: utf-8 -*-

from mock import (
    Mock,
)

USER_1 = Mock()

LANG_PAIR_EN_PL = 'en_pl'

PROGRESSION_1 = Mock(
    user=USER_1,
    lang_pair=LANG_PAIR_EN_PL,
)

DATASET_1 = Mock(
    lang_pair=LANG_PAIR_EN_PL,
)

# Word Pairs

WP_10 = Mock(base=u'dog', target=u'pies')
WP_11 = Mock(base=u'cat', target=u'kot')
WP_12 = Mock(base=u'lion', target=u'lew')
WP_13 = Mock(base=u'apple', target=u'jabłko')
WP_14 = Mock(base=u'porcupine', target=u'jeżozwierz')

# Links

L_10 = Mock(ds=DATASET_1, wp=WP_10)
L_11 = Mock(ds=DATASET_1, wp=WP_11)
L_12 = Mock(ds=DATASET_1, wp=WP_12)
L_13 = Mock(ds=DATASET_1, wp=WP_13)
L_14 = Mock(ds=DATASET_1, wp=WP_14)

LINKS_1 = [L_10, L_11, L_12, L_13, L_14]
