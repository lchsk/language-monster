# -*- encoding: utf-8 -*-

import xml.etree.cElementTree as ET
import MySQLdb as mdb
from sqlalchemy import update
from db.structure import *
from utility.utility import *
import os

# items to process from xml files before saving in db
CHUNK_SIZE = 5000000
# items to read from DB
YIELD_PER = 100000

class Popularity(object):
    def __init__(self, base, path):
        self.base = base
        self.path = path
        self.session = get_session()

        self.d = {}

        self.base_t = get_tables(self.base)

    def _count(self):
        if not os.path.exists(self.path):
            print 'Path {0} does not exist.'.format(self.path)
            return

        f = open(self.path)

        i = 0
        cnt = 0
        title = ''
        desc = ''

        for event, elem in ET.iterparse(f):
            cnt += 1
            if elem.tag[-5:] == "title":
                title = elem.text
            elif elem.tag[-4:] == "text":
                desc = elem.text

            if title and desc:
                try:
                    words = rm_nonalnum(desc.lower())

                    for w in words.split():
                        if w not in self.d:
                            self.d[w] = 0

                        self.d[w] += 1
                except Exception, e:
                    print str(e)

                title = ''
                desc = ''
            elem.clear()

        f.close()
        print self.d.items()[:20]

    def _save(self):
        words = self.session.query(
            self.base_t['data']
        ).filter(
            self.base_t['data'].language == self.base_t['own_name']
        )

        for i, w in enumerate(words):
            val = self.d.get(w.word.decode('utf-8').lower(), 0)

            if val:
                w.popularity = w.popularity + val

        print 'Committing...'
        self.session.commit()

    def run(self):
        start, p1 = get_time()
        print 'Start time: %s' % p1
        self._count()
        self._save()
        end, p2 = get_time()
        print 'End time: %s' % p2
        print 'Total time: %s' % (end - start)
