# -*- encoding: utf-8 -*-
from utility.utility import *
from set.maker import Maker
import pytest

class TestClass:
    def test_wordlist(self):

        a = get_word_list('a,b.c,d;e,f.g,h', ';,.')
        assert a == ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

        a = get_word_list('a,b.c,d;', ';,.')
        assert a == ['a', 'b', 'c', 'd']

        a = get_word_list('a,b.c,d', ',.')
        assert a == ['a', 'b', 'c', 'd']

        a = get_word_list('a,b,c,d', ',')
        assert a == ['a', 'b', 'c', 'd']

        a = get_word_list('a,b,c;d', ',;')
        assert a == ['a', 'b', 'c', 'd']

        a = get_word_list('a;b,c;d!e.f', ',;.!')
        assert a == ['a', 'b', 'c', 'd', 'e', 'f']

    def test_text(self):

        assert is_text_only('abc') == True
        assert is_text_only(u'abc 123') == True
        assert is_text_only('abc 123, ABC') == False
        assert is_text_only(u'abc 123 ABC ąśćżłó') == True

    def test_words_loader(self):
        '''
            Test whether number of words loaded is correct.
        '''

        m = Maker('en', 'es')
        m.get_words('Felids')

        assert len(m.results) == 12

    def test_context(self):

        assert is_context('{{l|en|yak}}') == True
        assert parse_direct_trans('{{l|en|yak}}', 'en') == 'yak'
        assert parse_direct_trans('{{l/en|olingo}}', 'en') == 'olingo'
