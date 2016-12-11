import pytest

from utility.settings import Settings
from db.structure import *

class TestClass:
    def test_settings(self):
        s = Settings()

        DBSession = sessionmaker(bind=get_engine())
        session = DBSession()

        langs = s.config['available_languages']

        for lang in langs.split(','):
            t = get_tables(lang)

            tables = ('raw', 'raw_table')

            assert t != None, 'Languages ' + lang + ' is not added in the list of tables in db.structure t dictionary.'

            for table in tables:
                assert t.get(table, None) != None

            try:
                res = session.query(t['raw']).first()
                print res
            except Exception, e:
                pytest.fail(str(e))
