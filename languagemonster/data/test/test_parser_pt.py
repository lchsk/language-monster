import pytest

from utility.settings import Settings
from db.structure import *
from parser.parser_pt import ParserPt

ACR = 'pt'

class TestParserPt:

    def setup(self):
        self.s = Settings()

        self.p = ParserPt(self.s, ACR)
        
        DBSession = sessionmaker(bind=get_engine())
        self.session = DBSession()
        
        self.t = get_tables(ACR)
        self.raw = self.t['raw']

    def get_row(self, word):
        return self.session.query(self.raw).filter(
            self.raw.word == word
        ).first()

        
    def test_get_languages1(self):
        resp = self.get_row('dog')
        assert '-en-' in self.p._get_languages(resp.desc)
        assert '-sv-' in self.p._get_languages(resp.desc)
        assert '-vo-' in self.p._get_languages(resp.desc)

    def test_get_languages2(self):
        resp = self.get_row('mama')
        
        langs = self.p._get_languages(resp.desc)
        
        assert len(langs) == 4
        assert '-pt-' in langs
        assert '-ja-' in langs
        
    def test_get_definition1(self):
        resp = self.get_row('dog')
        
        langs = self.p._get_languages(resp.desc)

        defs = self.p._get_definition(resp.desc, langs)
        
        assert len(defs) == 3

    def test_get_definition2(self):
        resp = self.get_row('mama')
        
        langs = self.p._get_languages(resp.desc)

        defs = self.p._get_definition(resp.desc, langs)
        
        assert len(defs) == 4
        
    def test_analyse_article(self):
        resp = self.get_row('dog')
        
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
        resp = self.get_row('dog')

        article = self.p._analyse_article(resp.desc)

        results = []

        for k, v in article.iteritems():
            for i in v:
                d = self.p._parse('dog', ACR, i)

                if d:
                    results.append(d)
        
        meaning = -1
        
        for r in results:
            for s in r:
                assert s['meaning'] == meaning + 1
                meaning += 1