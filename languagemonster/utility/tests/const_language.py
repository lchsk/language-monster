from mock import Mock

LANG_EN = Mock(acronym='en')
LANG_DE = Mock(acronym='de')
LANG_PL = Mock(acronym='pl')

BASE_GB = Mock(language=LANG_EN, country='gb', symbol='en_uk')
BASE_US = Mock(language=LANG_EN, country='us', symbol='en_us')
BASE_AU = Mock(language=LANG_EN, country='au', symbol='en_au')
BASE_DE = Mock(language=LANG_DE, country='de', symbol='de_de')
BASE_AT = Mock(language=LANG_DE, country='at', symbol='de_at')
BASE_PL = Mock(language=LANG_PL, country='pl', symbol='pl_pl')
