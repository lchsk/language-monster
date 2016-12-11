# -*- encoding: utf-8 -*-
import pytest

from utility.settings import Settings
from db.structure import *
from parser.parser_fr import ParserFr

ACR = 'fr'

class TestParserFr:

    def setup(self):
        self.s = Settings()

        self.p = ParserFr(self.s, ACR)
        
        DBSession = sessionmaker(bind=get_engine())
        self.session = DBSession()
        
        self.t = get_tables(ACR)
        self.raw = self.t['raw']

    def get_row(self, word):
        return self.session.query(self.raw).filter(
            self.raw.word == word
        ).first()

        
    def test_get_languages1(self):
        resp = self.get_row('cat')

        langs = self.p._get_languages(resp.desc)
        assert len(langs) > 2
        assert 'fr' in langs
        assert 'en' in langs

    def test_get_languages2(self):
        resp = self.get_row('dog')
        
        langs = self.p._get_languages(resp.desc)
        print langs
        assert len(langs) == 6
        assert 'vo' in langs
        assert 'en' in langs
        assert 'ro' in langs

    def test_get_definition1(self):
        resp = self.get_row('zrobić')
        
        langs = self.p._get_languages(resp.desc)
        defs = self.p._get_definition(resp.desc, langs)
        assert len(defs) == 1
        assert 'pl' in defs

    def test_get_definition2(self):
        resp = self.get_row('leer')
        
        langs = self.p._get_languages(resp.desc)

        defs = self.p._get_definition(resp.desc, langs)
        assert 'en' in defs
        assert 'es' in defs

    def test_analyse_article(self):
        resp = self.get_row('cat')
        
        article = self.p._analyse_article(resp.desc)
        for k, v in article.iteritems():
            for i in v:
                if i.line:
                    assert bool(i.head3) == True or bool(i.head4) == True
                    
        resp = self.get_row('mama')
        
        article = self.p._analyse_article(resp.desc)
        
        for k, v in article.iteritems():
            for i in v:
                if i.line:
                    assert bool(i.head3) == True or bool(i.head4) == True

    def test_parse(self):
        word = 'cat'

        resp = self.get_row(word)

        article = self.p._analyse_article(resp.desc)

        results = []

        for k, v in article.iteritems():
            for i in v:
                d = self.p._parse(word, ACR, i)

                if d:
                    results.append(d)
        
        for r in results:
            for a in r:
                print a['w1'], a['w2'], a['comments']
        
        meaning = -1
        
        for r in results:
            for s in r:
                assert s['meaning'] == meaning + 1
                meaning += 1
