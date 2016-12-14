# -*- encoding: utf-8 -*-
from utility.utility import *
from db.structure import *
from parser import Parser
import re

class Item(object):
    def __init__(self, line, head3, head4):
        self.line = line
        self.head3 = head3
        self.head4 = head4

    def __str__(self):
        return '{0} ({1}, {2})'.format(self.line, self.head3, self.head4)

    def __unicode__(self):
        return '{0} ({1}, {2})'.format(self.line, self.head3, self.head4)

class ParserPt(Parser):
    def __init__(self, settings, language):
        Parser.__init__(self, settings, language)
        self.meaning = 0

    def _get_languages(self, raw):
        languages = []
        # == {{-en-}} ==
        a = re.findall(r'^=.*?{{(-\w+-)}}.*?=$', raw, re.M | re.I | re.S | re.UNICODE)

        for _a in a:
            languages.append(_a)

        return languages

    def _get_definition(self, raw, languages):
        defs = {}

        for i, lang in enumerate(languages):
            if i == len(languages) - 1:

                # the last one

                r = re.findall(r'^=\s?\{\{' + lang + '\}\}\s?=(.*)', raw, re.M | re.I | re.S | re.UNICODE)
            else:
                
                # several languages
                
                r = re.findall(r'^=\s?\{\{' + lang + '\}\}\s?=(.*)=\s?\{\{' + languages[i + 1] + '\}\}\s?=', raw, re.M | re.I | re.S | re.UNICODE)

            if len(r) >= 1:
                defs[lang] = unicode(r[0])

        return defs

    def _analyse_article(self, raw):

        all_data = {}
        defs = self._get_definition(raw, self._get_languages(raw))

        for lang, val in defs.iteritems():

            head3, head4 = '', ''
            data = []

            for line in val.split('\n'):
                r3 = re.findall(r'^==([\w ]+)==.*?$', line, re.M | re.I | re.S | re.UNICODE)
                r4 = re.findall(r'^===([\w ]+)===.*?$', line, re.M | re.I | re.S | re.UNICODE)
                if r3:
                    head3 = unicode(r3[0])
                    head4 = ''
                elif r4:
                    head4 = unicode(r4[0])

                elif line:
                    data.append(Item(line, head3, head4))

            all_data[lang] = data

        return all_data

    def _insert(self, group):
        for g in group:
            item = self.data_table()
            item.language = g['lang']
            item.head3 = g['head3']
            item.head4 = g['head4']
            item.word = g['w1']
            item.word_lower = g['w1'].lower()
            item.definition = g['w2']
            item.meaning = g['meaning']
            item.comments = g['comments']
            item.dirty = g['dirty']
            
            self.session.add(item)


    def _parse(self, word, lang, item):

        sets = []

        if item.line.startswith('#'):
            text = item.line[1:]

            paren = get_context(text, '(', ')', 1)
            brack = get_context(text, '{', '}', 2)
            comments = paren + brack

            p = parse_link(rm(text, [paren, brack])).strip()

            words = get_word_list(p, None)

            for w in words:
                dirty = 'F' if is_text_only(w) else 'T'

                word_group = dict(
                    w1 = word,
                    lang = lang,
                    head3 = item.head3,
                    head4 = item.head4,
                    w2 = w,
                    meaning = self.meaning,
                    comments = ''.join(comments),
                    dirty = dirty
                )
                
                sets.append(word_group)
                self.meaning += 1
        return sets

    def run(self):
        start, p1 = get_time()
        print 'Start time: %s' % p1

        res = self.session.query(self.raw).yield_per(1000)

        for i, r in enumerate(res):
            if i % 100 == 0:
                print i
            if i % 1000 == 0:
                self.session.commit()
            
            self.meaning = 0
            all_data = self._analyse_article(r.desc)

            for lang, data in all_data.iteritems():
                for item in data:
                    group = self._parse(r.word, lang, item)
                    if group:
                        self._insert(group)
        self.session.commit()
        end, p2 = get_time()

        print 'End time: %s' % p2
        print 'Total time: %s' % (end - start)
