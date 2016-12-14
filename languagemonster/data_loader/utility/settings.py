import sys, os
import getopt
import argparse
from db.structure import create
from loader import Loader
from parser.parser import Parser
from parser.parser_en import ParserEn
from parser.parser_pl import ParserPl
from parser.parser_it import ParserIt
from parser.parser_pt import ParserPt
from parser.parser_de import ParserDe
from parser.parser_es import ParserEs
from parser.parser_fr import ParserFr

from set.popularity import Popularity
from set.maker import Maker

class Settings(object):
    def __init__(self):

        # parameters dictionary
        self.params = {}
        self.config = {}

        path = os.path.dirname(__file__)

        self.config_file = open(path + '/../config')
        self.read_config()
        self.config_file.close()

    def help(self):
        print 'Possible use cases:'
        print '(1) Create schema: --schema'
        print
        print '(2) Load from wiki'
        print '\t--language <acronym> --load <filepath>'
        print
        print '(3) Parse data'
        print '--parse  --language <acronym>'
        print
        print '(4) Compute popularity values'
        print '--popularity <path> --base <acronym>'
        print
        print '(5) Get dataset'
        print '--base <acronym> --target <acronym> --word_type <(Noun etc.)> --category <(Animals etc.)> --threshold <Popularity> --limit <limit> --out <filepath>'

        sys.exit(0)

    def empty(self, args):
        for arg in vars(args):
            if getattr(args, arg):
                return False

        return True

    def read_config(self):

        for line in self.config_file:
            if not line.startswith('#'):
                d = line.split('=')
                k, v = d[0].strip(), d[1].strip()
                self.config[k] = v

    def read_parameters(self):

        parser = argparse.ArgumentParser(description='')

        parser.add_argument('--explain', dest='explain', action="store_true", help='More help')
        parser.add_argument('--schema', dest='schema', action="store_true", help='Create schema')
        parser.add_argument('--parse', dest='parse', action="store_true", help='Parse data')

        # (2)
        parser.add_argument('--language', action="store", dest="language", help='Language (acronym)')
        parser.add_argument('--load', action="store", dest="load", help='Load wikitionary. Argument is file path')

        # (4) Popularity values
        parser.add_argument('--popularity', action="store", dest="popularity", help='Compute popularity values')
        parser.add_argument('--base', action="store", dest="base_lang", help='Base language')
        parser.add_argument('--target', action="store", dest="target_lang", help='Target language')

        # (5) Get dataset
        parser.add_argument('--word_type', action="store", dest="word_type", help='Word type (noun etc.)')
        parser.add_argument('--category', action="store", dest="category", help='Category (eg. Animals)')
        parser.add_argument('--threshold', action="store", dest="threshold", help='Popularity threshold')
        parser.add_argument('--limit', action="store", dest="limit", help='Number of words returned')

        parser.add_argument('--out', action="store", dest="out", help='Output filepath')

        parser.add_argument('--exported-file', action="store", dest="exported_file", help='Load exported file')

        parser.add_argument('--from-file', action="store", dest="from_file", help='Load text file')


        args = parser.parse_args()
        # print args

        # Check if language is correct
        if args.language and args.language not in self.config['available_languages'].split(','):
            print '"%s" does not exist. Available languages: %s' % (args.language, self.config['available_languages'])

        # (1) Create schema
        elif args.schema:
            create()

        # (2) Load from wiki
        elif args.language and args.load:
            l = Loader(args.load, args.language)
            l.load_wiki()

        # (3)
        elif args.parse and args.language:
            p = self._get_parser(args.language)
            p.run()

        # (4)
        elif args.popularity and args.base_lang:
            po = Popularity(args.base_lang, args.popularity)
            po.run()

        # (5)
        elif all((
            args.base_lang,
            args.target_lang,
            args.word_type,
            args.category
        )) and not args.exported_file:
            m = Maker(
                args.base_lang,
                args.target_lang,
                args.word_type,
                args.out,
                args.category
            )
            m.translation()

        # (6)
        # from exported text file
        elif args.base_lang and args.target_lang and args.exported_file:
            print 'From exported text file'
            # load and translate exported json data
            m = Maker(
                args.base_lang,
                args.target_lang,
                args.word_type,
                args.out,
                args.category
            )
            m.from_exported_file = True
            m.translate_exported_file(args.exported_file)

        # (7)
        # from a text file
        elif args.base_lang and args.target_lang and args.from_file:
            m = Maker(
                args.base_lang,
                args.target_lang,
                args.word_type,
                args.out,
                None
            )
            m.from_text_file = True
            m.translate_text_file(args.from_file)

        else:
            self.help()

    def _get_parser(self, language):
        if language == 'en':
            return ParserEn(self, language)
        elif language == 'pl':
            return ParserPl(self, language)
        elif language == 'it':
            return ParserIt(self, language)
        elif language == 'pt':
            return ParserPt(self, language)
        elif language == 'de':
            return ParserDe(self, language)
        elif language == 'es':
            return ParserEs(self, language)
        elif language == 'fr':
            return ParserFr(self, language)

    def print_parameters(self):
        print 'Parameters:'
        for k, v in self.params.iteritems():
            print '\t' + k + ': ' + str(v)
