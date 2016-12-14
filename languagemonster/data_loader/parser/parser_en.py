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

class ParserEn(Parser):
    def __init__(self, settings, language):
        Parser.__init__(self, settings, language)

    def _get_languages(self, raw):
        languages = []

        a = re.findall(r'^==([\w\s]+)==$', raw, re.M | re.I | re.S | re.UNICODE)

        for _a in a:
            languages.append(_a)

        return languages

    def _get_definition(self, raw, languages):
        defs = {}

        for i, lang in enumerate(languages):
            if i == len(languages) - 1:
                r = re.findall(r'^==' + lang + '==(.*)', raw, re.M | re.I | re.S | re.UNICODE)
            else:
                r = re.findall(r'^==' + lang + '==(.*)==' + languages[i + 1] + '==', raw, re.M | re.I | re.S | re.UNICODE)

            if len(r) >= 1:
                defs[lang] = unicode(r[0])

        return defs

    def _analyse_article(self, raw):

        all_data = {}
        defs = self._get_definition(raw, self._get_languages(raw))

        for lang, val in defs.iteritems():
            head3, head4 = '', ''
            # data = {}
            data = []
            for line in val.split('\n'):
                r3 = re.findall(r'^===([\w\s]+)===$', line, re.M | re.I | re.S | re.UNICODE)
                r4 = re.findall(r'^====([\w\s]+)====$', line, re.M | re.I | re.S | re.UNICODE)
                if r3:
                    head3 = unicode(r3[0])
                    head4 = ''
                    # data.append(Item(line, head3))
                elif r4:
                    head4 = unicode(r4[0])

                elif line:
                    # data[topic].append(line)
                    data.append(Item(line, head3, head4))
                    # print line

            all_data[lang] = data

        return all_data

    def _insert(self, lang, head3, head4, word, definition, meaning, comments, dirty):
        item = self.data_table(lang, head3, head4, word, definition, meaning, comments, dirty)
        self.session.add(item)


    def _parse(self, word, lang, item):

        meaning = 0
        # for v in item.line:
        if item.line.startswith('#'):
        # if re.findall(r'^#([\w\s]+)===$', item.line, re.M | re.I | re.S | re.UNICODE)
            text = item.line[1:]

            paren = get_context(text, '(', ')', 1)
            brack = get_context(text, '{', '}', 2)
            # ref = get_context(text, '<ref>', '</ref>', 1)
            comments = paren + brack

            p = parse_link(rm(text, [paren, brack])).strip()

            words = get_word_list(p, None)

            for w in words:
                dirty = 'F' if is_text_only(w) else 'T'
                self._insert(lang.strip(), item.head3.strip(), item.head4.strip(), word.strip(), w.strip(), meaning, ''.join(comments), dirty)
                # print word, lang, item.head3, item.head4, w, meaning, ''.join(comments), dirty
            meaning += 1

    def run(self):
        start, p1 = get_time()
        print 'Start time: %s' % p1

        res = self.session.query(self.raw).yield_per(1000)

        for i, r in enumerate(res):
            if i % 100 == 0:
                print i
            if i % 1000 == 0:
                self.session.commit()

            all_data = self._analyse_article(r.desc)

            for lang, data in all_data.iteritems():
                for item in data:
                    self._parse(r.word, lang, item)

        end, p2 = get_time()
        print 'End time: %s' % p2
        print 'Total time: %s' % (end - start)
