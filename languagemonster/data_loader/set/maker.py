# -*- encoding: utf-8 -*-
import logging
import os
import sys
import json

from sqlalchemy import (
    func,
    or_,
)

from db.structure import *
from utility.utility import *

from set.outitem import OutItem
from validation import comparison
from conf import languages
from conf.languages import (
    defs,
    POS,
    Slang,
)

# If set to true, English wiki will be used as an intermediate translation
# in case words are not found in base/target wikis

USE_ENGLISH = True
REMOVE_SLANG = True

logger = logging.getLogger(__name__)

class Maker(object):
    def __init__(self, base, target, p_type, output, category):
        self.session = get_session()
        self.results = []
        self.base = base
        self.target = target
        self.from_exported_file = False
        self.from_text_file = False

        # final output; consists of OutItem objects

        self.items = set()
        self._errors = []

        for lang in languages.WORKING_LANGUAGES:
            try:
                languages.validate(lang)
            except Exception as e:
                logger.critical(
                    'Language validation error in definition of "%s"',
                    lang,
                )
                logger.critical('%s', e)
                sys.exit(1)

        # Set to True if target is English

        self.reversed = False
        self.no_english = False

        if 'en' not in (self.base, self.target):
            self.no_english = True

        self.actual_base = self.base

        self.results_dir = 'output'

        self.base_config = languages.t[base]
        self.target_config = languages.t[target]
        self.english_config = languages.t['en']

        # eg. Animals

        self.category = category

        # eg. Noun
        self.type = p_type

        self.outfile = None

        if output:
            self.output = output
        else:
            self.output = "{filename}.txt".format(filename = category)

        first = self.base
        second = self.target

        self.output_dir = '{0}/{1}/{2}'.format(self.results_dir, first, second)
        self.output_filepath = '{0}/{1}/{2}/{3}'.format(
            self.results_dir,
            first,
            second,
            self.output
        )

        try:
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)
        except OSError as exception:
            raise

        if self.output:
            self.outfile = open(self.output_filepath, 'w')
        else:
            logger.critical('Problem with opening and output file')
            sys.exit(1)

        self.t = get_tables(self.base)
        self.t_target = get_tables(self.target)

        if self.no_english:
            self.t_actual = get_tables(self.actual_base)
            self.data_table_actual = self.t_actual['data']

        self.english_tables = get_tables('en')
        self.english_data = self.english_tables['data']
        self.data_table = self.t['data']
        self.target_data_table = self.t_target['data']

    def get_words(self, term):
        target_term = self._create_term(term)

        cc = self.session.query(CategoryLinksEn).filter(
            CategoryLinksEn.cl_to == target_term
        )

        for c in cc:
            if c.cl_type == 'subcat':
                self.get_words(c.cl_sortkey_prefix)
            elif c.cl_type == 'page':
                if c.cl_sortkey_prefix:
                    self.results.append(c.cl_sortkey_prefix.decode('utf-8').lower())
                else:
                    self.results.append(c.cl_sortkey.decode('utf-8').lower())

    def _create_term(self, term):
        return '{0}:{1}'.format(self.target, term)

    def _get_direct_translation(self, _list, acronym):
        ''' eg. yak -> yak '''

        for i in _list:
            p = parse_direct_trans(i, acronym)
            if p:
                return p

        return None

    def _save_metadata(self):
        '''
            Adds dataset metadata to the output file.
            Eg. language, dataset name etc.
        '''

        if self.no_english:
            self.outfile.write('#base={0}\n'.format(self.actual_base))
            self.outfile.write('#target={0}\n'.format(self.target))
        elif self.reversed:
            self.outfile.write('#base={0}\n'.format(self.target))
            self.outfile.write('#target={0}\n'.format(self.base))
        else:
            self.outfile.write('#base={0}\n'.format(self.base))
            self.outfile.write('#target={0}\n'.format(self.target))

        self.outfile.write('#pos={0}\n'.format(self.type if self.type else ''))
        self.outfile.write('#name_en={0}\n'.format(self.category))
        self.outfile.write('#from_exported_file={0}\n'.format(
            str(self.from_exported_file))
        )
        self.outfile.write('#{0}'.format(OutItem.LINE))

    def _translate(
        self,
        to_translate,
        data_table,
        base_config,
        target_config,
        validate = False
    ):
        self._errors = []
        _type = base_config.get('pos', {}).get(self.type, {})

        meaning = base_config.get('meaning')

        if not _type:
            _type = meaning

            logger.info('Type not provided using meaning: "%s"', _type)

        _language = base_config['languages'][target_config['acronym']]
        _items = set()

        logger.info('Number of words to translate: %s', len(to_translate))
        logger.info(
            'Using language "%s", type "%s"',
            _language,
            _type.encode('utf-8') if _type else None,
        )
        logger.info('Using data table "%s"', data_table)

        for word, pos in to_translate:
            logger.info('=' * 80)
            logger.info('Init word "%s"', word)

            if pos:
                if pos not in POS:
                    logger.critical('Invalid POS "%s" for word "%s"', pos, word)

                    sys.exit(1)

                pos = base_config.get('pos', {}).get(pos)

                logger.info(
                    'Found POS definition for "%s", new pos: "%s"',
                    word,
                    pos
                )
            else:
                pos = meaning

            q = self.session.query(
                data_table
            ).filter(
                data_table.word_lower == word.lower()
            ).filter(
                or_(
                    data_table.head3.ilike(u'%{0}%'.format(pos)),
                    data_table.head4.ilike(u'%{0}%'.format(pos)),
                    pos is None
                )
            ).filter(
                data_table.language == _language
            ).filter(
                or_(
                    data_table.definition != '',
                    # data_table.comments != ''
                )
            )
            # .group_by(
                # data_table.word_lower, data_table.head3, data_table.head4
            # )

            logger.info('Executing query: \n%s', get_mysql_query_with_params(q))

            rs = q.all()

            rs_cnt = len(rs)

            if rs_cnt:
                logger.info('Loaded %s results from database', rs_cnt)
            else:
                logger.error(
                    'No data found in database for word "%s" ("%s")',
                    word,
                    pos,
                )

                self._errors.append((word, pos))

            tmp_results = []

            def cond(r):
                head3 = unicode(r.head3, 'utf-8')
                head4 = unicode(r.head4, 'utf-8')

                if not r or not word or is_no_text(r.definition):
                    return False
                if not (head3 or head3):
                    return False

                if _type is not None and not (pos in head3 or pos in head4):
                    return False

                return True

            for r in rs:
                if cond(r):
                    pop = self.session.query(
                        self.t_target['data']
                    ).filter(
                        self.t_target['data'].word_lower == r.word_lower
                    ).first()

                    r.pop = pop.popularity if pop else 0

                    tmp_results.append(r)

            for r in tmp_results:
                if validate:
                    # only for en and validation
                    # check for things like that: {{l|en|rabbit}}
                    # in comments

                    comments_trans = self._direct_trans(r.comments)

                    b = r.definition

                    if comments_trans:
                        b += comments_trans
                else:
                    b = r.definition

                logger.info('Base: %s, def: %s, word: %s', b, r.definition, r.word)

                comments = read_comments(r.comments)

                omit = False

                if comments:
                    logger.info('Found comments: %s', comments)

                    if REMOVE_SLANG:
                        for slang in Slang:
                            if slang in comments:
                                logger.info(
                                    'Slang word found: "%s" = "%s", omitting',
                                    b,
                                    r.word.decode('utf-8'),
                                )

                                omit = True
                                break

                if omit:
                    continue

                _items.add(
                    OutItem(
                        b=b,
                        t=r.word.decode('utf-8'),
                        p=r.pop,
                        c=comments,
                        pos=self._read_pos(r),
                        id_=r.id,
                    )
                )

        return _items

    def _read_pos(self, row):


        head3 = row.head3.lower()
        head4 = row.head4.lower()

        for en_pos, POS in defs[self.target]['pos'].iteritems():
            pos = POS.encode('utf-8').lower()

            if pos in head3 or pos in head4:
                return en_pos

        return ''

    def _missed_words(self, result, argument):
        """
            finds words that were missed in translation; after using:
            argument: list of words
            result: list of translated words
            TODO: merge with _missed_words()
        """

        items = [ i.t for i in result ]

        to_translate = []

        for r in argument:
            if r not in items:
                to_translate.append(r)

        return to_translate

    def _direct_trans(self, comments):
        """
            for getting translation from shit like this:
            {{l|en|rabbit}}
        """
        ver1 = re.findall(r'\{\{l\|\w+\|([\w\s]+)\}\}', comments)
        ver2 = re.findall(r'\{\{l\/\w+\|([\w\s]+)\}\}', comments)

        return ', '.join(ver1) + ', '.join(ver2)

    def translate_exported_file(self, file_path):
        """
        Translates json file with keys: etarget, ebase
        """

        if os.path.exists(file_path):
            with open(file_path) as f:
                # we assume content is en -> eng exported file
                content = json.loads(f.read())
                to_be_translated = [wp['etarget'] for wp in content]

                if self.base == 'en':
                    logger.info("Base = en")

                    items = self._translate(
                        to_translate = to_be_translated,
                        data_table = self.target_data_table,
                        base_config = self.target_config,
                        target_config = self.base_config,
                    )

                    self.get_words(self.category)

                    from_target = self._translate(
                        to_translate = self.results,
                        data_table = self.data_table,
                        base_config = self.english_config,
                        target_config = self.target_config,
                    )

                    for i in items:
                        i.switch()

                        self.items = list(items) + list(from_target)

                else:
                    logger.info("No english")
                    # here: base, target != english
                    target_en = self._translate(
                        to_translate = to_be_translated,
                        data_table = self.target_data_table,
                        base_config = self.target_config,
                        target_config = self.english_config,
                    )

                    target_items = [wp.b for wp in target_en]
                    en_items = [wp.t for wp in target_en]

                    logger.info('Number of target items: %s', len(target_items))

                    base_en = self._translate(
                        to_translate = en_items,
                        data_table = self.data_table,
                        base_config = self.base_config,
                        target_config = self.english_config,
                    )

                    logger.info('Number of base items: %s', len(base_en))

                    cnt = 0
                    self.items = []
                    for i in target_en:
                        for j in base_en:
                            if i.t == j.t:
                                self.items.append(OutItem(
                                    b=j.b,
                                    t=i.b,
                                    e=i.t,
                                    i=True,
                                    c='',
                                    p=0,
                                    pos=i.pos,
                                ))
                                # cnt += 1

                    logger.info('Number of items: %s', len(self.items))

                    self.clean()
                    self.save()
        else:
            logger.info('Path %s does not exist', file_path)

    def translate_text_file(self, file_path):
        """
        Translates text file with words in separate lines
        """

        logger.info('Translating file "%s"', file_path)

        if os.path.exists(file_path):
            with open(file_path) as f:

                to_be_translated = []

                for line in f:
                    tokens = line.split('||')

                    if not tokens:
                        continue

                    word = tokens[0].strip()
                    pos = ''

                    if len(tokens) == 2:
                        pos = tokens[1].strip()

                    to_be_translated.append((word, pos))

                items = self._translate(
                    to_translate = to_be_translated,
                    data_table = self.target_data_table,
                    base_config = self.target_config,
                    target_config = self.base_config,
                )

                for i in items:
                    i.switch()

                self.items = list(items)
                self.clean()
                self.save()
        else:
            logger.warning('Path %s does not exist', file_path)

    def translation(self):

        self.get_words(self.category)

        _items = self._translate(
            to_translate = self.results,
            data_table = self.data_table,
            base_config = self.base_config,
            target_config = self.target_config,
        )

        _to_translate = self._missed_words(_items, self.results)

        self.items = list(_items)

        if USE_ENGLISH and self.no_english and len(_to_translate) > 0:

            # use English wiki to translate the rest

            _english = self._translate(
                to_translate = _to_translate,
                data_table = self.english_data,
                base_config = self.english_config,
                target_config = self.target_config,
            )

            _en_target = {}

            for e in _english:

                # English -> Target

                _en_target[e.b] = e.t

            _target = self._translate(
                to_translate = _en_target.keys(),
                data_table = self.data_table,
                base_config = self.base_config,
                target_config = self.english_config,
            )

            # base -> target (final version obtained from English)

            _b_t = []

            for en, ta in _en_target.iteritems():
                for i in _target:
                    if i.t == en:
                        _b_t.append(
                            OutItem(
                                b=i.b,
                                t=ta,
                                e=en,
                                i=True,
                                c=i.c + u'{{from_english}}',
                                p=i.p,
                                pos=i.pos,
                            )
                        )

            # don't add duplicates

            for i in _b_t:
                if i not in self.items:
                    self.items.append(i)

        self.clean()
        self.validate()
        self.save()
        # run final comparison of word/definition pairs and values from the DB

        # comparison.compare(self.session, self.t_target, out)

    def clean(self):

        # characters to remove

        CHARS = (
            # "'",
            '"',
            '(',
            ')',
            '[',
            ']'
        )

        for i in self.items:
            for c in CHARS:
                i.b = i.b.replace(c, '')
                i.t = i.t.replace(c, '')

            i.b = i.b.strip()
            i.t = i.t.strip()

            # last period
            if i.b and i.b[-1] == '.':
                i.b = i.b[:-1]

            if i.t and i.t[-1] == '.':
                i.t = i.t[:-1]

            # remove xml tags
            i.b = re.sub(r'<.+>', '', i.b)
            i.t = re.sub(r'<.+>', '', i.t)

            # strip

            i.b = i.b.strip()
            i.t = i.t.strip()

            # check for duplicates

            for j in self.items:
                if i.b == j.b and i.t == j.t and i is not j:
                    self.items.remove(j)

    def validate(self):
        """
            runs a simple validation of base/target items
        """

        _base = [ i.b for i in self.items ]
        _target = [ i.t for i in self.items ]

        # base in English

        _base_e = self._translate(
            to_translate = _base,
            data_table = self.english_data,
            base_config = self.english_config,
            target_config = self.base_config,
            validate = True
        )

        _target_e = self._translate(
            to_translate = _target,
            data_table = self.english_data,
            base_config = self.english_config,
            target_config = self.target_config,
            validate = True
        )

        _base_d, _target_d = {}, {}

        for i in _base_e:
            _base_d[i.t] = i.b

        for i in _target_e:
            _target_d[i.t] = i.b

        # i is OutItem

        for i in self.items:
            if not i.e:
                i.e = _base_d.get(i.b, False) or _target_d.get(i.t, '')

            _base_check = unicode(_base_d.get(i.b, -1))
            _target_check = unicode(_target_d.get(i.t, 1))

            # verified

            VER = True

            if not _base_check or not _target_check:
                VER = False

            # mild condition

            if _base_check.lower() not in _target_check.lower() and \
                _target_check.lower() not in _base_check.lower():
                VER = False

            # if  _base_check == _target_check:

            if VER:
                i.c += '{{verified}}'
            else:
                i.c += '{{english_invalid}}'

                # if _base_check != u'-1':
            i.c += u'{{base={0}}}'.format(_base_check)
                # if _target_check != u'-1':
            i.c += u'{{target={0}}}'.format(_target_check)

    def save(self):
        self._save_metadata()
        length = len(self.items)

        self.items.sort(key=lambda x: x.b and x.id_)

        for item in self.items:
            self.outfile.write(item.line())

        logger.info('=' * 80)
        logger.info('Results saved %s', self.output_filepath)
        logger.info('Number of words: %s', length)
        logger.info('Words not found: %s', len(self._errors))

        errors = u', '.join(
            u'{} ({})'.format(word, pos)
            for word, pos in self._errors
        )

        logger.info('Errors: %s', errors)

        self.outfile.close()
