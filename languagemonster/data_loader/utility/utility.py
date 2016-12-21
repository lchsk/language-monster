# -*- encoding: utf-8 -*-

import time
import datetime
import re
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def get_engine():
    return create_engine(
        'mysql://{user}:{password}@localhost/{name}?charset=utf8'.format(
            user=os.getenv('LM_DATA_DB_USER'),
            password=os.getenv('LM_DATA_DB_PASS'),
            name=os.getenv('LM_DATA_DB_NAME'),
        )
    )

def get_session():
    return sessionmaker(bind=get_engine())()

def get_time():
    return datetime.datetime.now(), time.strftime(
        '%a, %d %b %Y %H:%M:%S +0000', time.localtime()
    )

def rm_brackets(d, symbol='[', count = 2):
    if symbol == '[' and count == 2:
        return (d.replace('[[', '')).replace(']]', '')
    elif symbol == '{' and count == 2:
        return (d.replace('{{', '')).replace('}}', '')

def get_context(d, beg, end, n):
    a = b = ''

    for i in xrange(0, n):
        a += '\\' + beg
        b += '\\' + end

    return re.findall(r'(' + a + '.+?' + b + ')', d)

def rm_re(regexp, where):
    """
        removes regular expression from a string
    """

    return re.sub(regexp, '', where)

def startswith(regexp, where):
    """
        true if string starts with regexp
    """

    return True if re.match(regexp, where, re.M | re.I | re.S | re.UNICODE) else False

def rm(d, what):
    _d = d

    if isinstance(what, (list, tuple)):
        for w in what:
            for i in w:
                _d = _d.replace(i, '')
        return _d
    elif isinstance(d, (str)):
        for w in what:
            return _d.replace(w, '')

def is_context(text):
    ''' Whether text contains only {{Something}}'''
    return True if re.match(r'^\{\{.+\}\}$', text, re.M | re.I | re.S | re.UNICODE) else False

def rm_nonalnum(s):
    """
    Removes non-alphanumeic characters from a string
    """

    delchars = u'!"#$%&\'()*+,-./:;=>?@[\\]^_`{|}~'
    # translate_to = None

    for c in delchars:
        s = s.replace(c, '')

    return s

def contains_context(text):
    ''' Whether text contains {{Something}} among others.
    '''
    pass

def get_language_context(text):
    '''
    '''
    pass

def is_text_only(text):
    return True if re.match(r'^[\w\s]+$', text, re.M | re.I | re.S | re.UNICODE) else False

def is_text_plus_only(text):
    return True if re.match(r'^[\w\s,.;!?-]+$', text, re.M | re.I | re.S | re.UNICODE) else False

def is_no_text(text):
    return True if re.match(r'^[^\w]+$', text, re.M | re.I | re.S | re.UNICODE) else False

def get_word_list(text, dividers):

    if not dividers:
        return [text]

    n = len(dividers)
    tmp = text.split(dividers[0])

    for i in dividers[1:]:
        _tmp = []
        for item in tmp:
            t = item.split(i)
            for _t in t:
                if _t:
                    _tmp.append(_t.strip())
        tmp = list(_tmp)

    return tmp

def parse_link(d, symbol = '[', count = 2):
    """
        gets translation from wiki syntax
    """

    repl_list = {}

    if symbol == '[' and count == 2:
        links = re.findall(r'(\[\[.+?\]\])', d, re.M | re.I | re.S | re.UNICODE)
    elif symbol == '{' and count == 2:
        links = re.findall(r'(\{\{.+?\}\})', d, re.M | re.I | re.S | re.UNICODE)

    for link in links:
        if '|' in link:
            repl_list[link] = rm_brackets(link.split('|')[1], symbol = symbol, count = count)
        else:
            repl_list[link] = rm_brackets(link, symbol = symbol, count = count)

    for k, v in repl_list.iteritems():
        d = d.replace(k, v)

    return d

def parse_smart(d):
    """
        tries to parse translation using both [[]] and {{}}
    """

    if re.match(r'.*?(\[\[.+?\]\]).*?', d, re.M | re.I | re.S | re.UNICODE):
        return parse_link(d, symbol='[', count=2)
    elif re.match(r'.*?(\{\{.+?\}\}).*?', d, re.M | re.I | re.S | re.UNICODE):
        return parse_link(d, symbol='{', count=2) 

    return d

def parse_direct_trans(c, lang):
    '''
        Get text from structures such as:
            - {{l/en|margay}}
            - {{l|en|coyote}}
        Should be removed(?)
    '''
    check = is_context(c)

    if check:
        tmp = c
        tmp = tmp.replace('{{', '')
        tmp = tmp.replace('}}', '')

        d = tmp.split('|')

        if len(d) == 2:
            if d[0] == ('l/' + lang):
                return d[1]
        elif len(d) == 3:
            if d[0] == 'l' and d[1] == lang:
                return d[2]
        else:
            return None

    return None