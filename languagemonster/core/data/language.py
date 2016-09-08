# -*- coding: utf-8 -*-

from collections import namedtuple

class Language(namedtuple('Language', [
    'english_name',
    'original_name',
    'acronym',
    'slug',
    'image_filename',
    'flag_filename',
])):
    __slots__ = ()

    def __unicode__(self):
        return u'{}'.format(self.english_name)

pl = Language(
    english_name=u"Polish",
    original_name=u"Polski",
    acronym=u"pl",
    slug=u"polish",
    image_filename=u"poland",
    flag_filename=u"pl"
)

pt = Language(
    english_name=u"Portuguese",
    original_name=u"Português",
    acronym=u"pt",
    slug=u"portuguese",
    image_filename=u"portugal",
    flag_filename=u"pt"
)

fr = Language(
    english_name=u"French",
    original_name=u"Français",
    acronym=u"fr",
    slug=u"french",
    image_filename=u"france",
    flag_filename=u"fr"
)

es = Language(
    english_name=u"Spanish",
    original_name=u"Español",
    acronym=u"es",
    slug=u"spanish",
    image_filename=u"spain",
    flag_filename=u"es"
)

en = Language(
    english_name=u"English",
    original_name=u"English",
    acronym=u"en",
    slug=u"english",
    image_filename=u"uk",
    flag_filename=u"uk"
)

it = Language(
    english_name=u"Italian",
    original_name=u"Italiano",
    acronym=u"it",
    slug=u"italian",
    image_filename=u"italy",
    flag_filename=u"it"
)

de = Language(
    english_name=u"German",
    original_name=u"Deutsch",
    acronym=u"de",
    slug=u"german",
    image_filename=u"germany",
    flag_filename=u"de"
)

LANGUAGES = dict(
    pl=pl,
    en=en,
    pt=pt,
    fr=fr,
    it=it,
    de=de,
    es=es,
)

# 65;"Danish";"Dansk";"dk";"danish";"denmark";"dk"
# 64;"Latin";"lingua latīna";"la";"latin";"latin";"la"
# 63;"Russian";"ру́сский";"ru";"russian";"russia";"ru"
# 62;"Belarusian";"Belarusian";"by";"belarusian";"belarus";"by"
# 61;"Slovene";"Slovene";"si";"slovene";"slovenia";"si"
# 60;"Bosnian";"Bosnian";"ba";"bosnian";"bosnia";"ba"
# 59;"Georgian";"Georgian";"ge";"georgian";"georgia";"ge"
# 58;"Kazakh";"Kazakh";"kz";"kazakh";"kazakhstan";"kz"
# 57;"Croatian";"Croatian";"hr";"croatian";"croatia";"hr"
# 56;"Armenian";"Armenian";"am";"armenian";"armenia";"am"
# 55;"Albanian";"Albanian";"al";"albanian";"albania";"al"
# 54;"Bulgarian";"Bulgarian";"bg";"bulgarian";"bulgaria";"bg"
# 53;"Serbian";"Serbian";"rs";"serbian";"serbia";"rs"
# 52;"Turkish";"Turkish";"tr";"turkish";"turkey";"tr"
# 51;"Greek";"Greek";"gr";"greek";"greece";"gr"
# 50;"Romanian";"Romanian";"ro";"romanian";"romania";"ro"
# 49;"Dutch";"Dutch";"nl";"dutch";"netherlands";"nl"
# 48;"Latvian";"Latvian";"lv";"latvian";"latvia";"lv"
# 47;"Estonian";"Estonian";"ee";"estonian";"estonia";"ee"
# 46;"Lithuanian";"Lithuanian";"lt";"lithuanian";"lithuania";"lt"
# 45;"Slovak";"Slovak";"sk";"slovak";"slovakia";"sk"

# 43;"Czech";"Czech";"cz";"czech";"czech";"cz"
# 42;"Ukrainian";"Ukraine";"ua";"ukrainian";"ukraine";"ua"
# 41;"Hungarian";"Hungary";"hu";"hungarian";"hungary";"hu"
# 40;"Japanese";"Japanese";"jp";"japanese";"japan";"jp"
# 39;"Finnish";"Finland";"fi";"finnish";"finland";"fi"
# 38;"Swedish";"Swedish";"se";"swedish";"sweden";"se"
# 37;"Norwegian";"Norwegian";"no";"norwegian";"norway";"no"
