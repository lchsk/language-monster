# -*- coding: utf-8 -*-

from db.structure import *
from utility import *
import xml.etree.cElementTree as ET
import MySQLdb as mdb

class Loader(object):
    def __init__(self, path, lang):
        self.path = path
        self.lang = lang

    def load_wiki(self):
        print 'loading ' + self.path + ' lang: ' + self.lang
        start, p1 = get_time()
        print 'Start time: %s' % p1

        con = mdb.connect(
            'localhost',
            'USER',
            'PASSWORD',
            'DB_NAME',
            use_unicode=True,
            charset='utf8'
        )

        t = get_tables(self.lang)
        raw = t['raw']
        raw_table = t['raw_table']

        f = open(self.path)

        with con:
            cur = con.cursor()

            con.set_character_set('utf8')
            cur.execute('SET NAMES utf8;')
            cur.execute('SET CHARACTER SET utf8;')
            cur.execute('SET character_set_connection=utf8;')

            cur.execute('truncate table %s;' % raw_table)

            word = ''
            desc = ''

            for event, elem in ET.iterparse(f):
                if elem.tag[-5:] == "title":
                    word = elem.text
                elif elem.tag[-4:] == "text":
                    desc = elem.text

                if word and desc:
                    # item = raw(word, desc)
                    # session.add(item)
                    try:
                        cur.execute("insert into `" + raw_table + "` (`word`, `desc`) values(%s, %s)", (word, desc))
                    except Exception, e:
                        print 'Error: ' + str(e) + ' on WORD: ' + word + ' DESC: ' + desc
                        print '\n\n'

                    word = ''
                    desc = ''
                elem.clear()

            f.close()
            end, p2 = get_time()
            print 'End time: %s' % p2
            print 'Total time: %s' % (end - start)
