# -*- encoding: utf-8 -*-

class OutItem(object):

    LINE = u"{base}||{target}||{pop}||{english}||{comments}||{pos}\n"

    def __init__(self, b, t, pos=None, e='', c='', i=False, p=0, id_=0, gloss=None):

        # word in base language

        self.b = b

        # word in target language

        self.t = t

        # word in English

        self.e = e

        # popularity

        self.p = p

        # comment

        self.c = c

        # true if is uses English

        self.i = i

        self.pos = pos

        # Database id
        self.id_ = id_

        self.gloss = gloss

        self.extra = None

    def __eq__(self, other):
        return all((
            self.b == other.b,
            self.t == other.t,
            self.pos == other.pos,
        ))

    def __hash__(self):
        return hash(self.b + self.t + self.pos)

    def switch(self):
        """
        Switch base <-> target
        """
        self.b, self.t = self.t, self.b

    def line(self):

        self.c = self.c.replace('||', '\|\|')

        _text = OutItem.LINE.format(
            base=self.b,
            target=self.t,
            english=self.e,
            comments=self.c,
            pop=self.p,
            pos=self.pos,
        )
        return _text.encode('utf-8')

    def __str__(self):
        return self.line()

    def __repr__(self):
        return self.line()

    # def __str__(self):
    #     return self.b.encode('utf-8') + ' -> ' + self.t.encode('utf-8') + ' /' + str(self.p)
