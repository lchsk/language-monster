# -*- encoding: utf-8 -*-
from utility.utility import *
from db.structure import *
import re

class Parser(object):
    def __init__(self, settings, language):
        self.settings = settings
        self.language = language
        self.session = get_session()

        self.t = get_tables(self.language)
        self.raw = self.t['raw']
        self.raw_table = self.t['raw_table']
        self.data_table = self.t['data']

    def run(self):
        pass

    def _get_languages(self, raw):
        pass

    def _get_definition(self, raw, languages):
        pass

    def _analyse_article(self, raw):
        pass

    def _insert(self):
        pass

    def _parse(self):
        pass
