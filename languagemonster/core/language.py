# -*- coding: utf-8 -*-

from collections import namedtuple

Language = namedtuple('Language', [
    'english_name',
    'original_name',
    'acronym',
    'slug',
    'image_filename',
    'flag_filename',
])

pl = Language(
    english_name="Polish",
    original_name=u"Polski",
    acronym="pl",
    slug="polish",
    image_filename="poland",
    flag_filename="pl"
)

pt = Language(
    english_name="Portuguese",
    original_name=u"Português",
    acronym="pt",
    slug="portuguese",
    image_filename="portugal",
    flag_filename="pt"
)

fr = Language(
    english_name="French",
    original_name=u"Français",
    acronym="fr",
    slug="french",
    image_filename="france",
    flag_filename="fr"
)

es = Language(
    english_name="Spanish",
    original_name=u"Español",
    acronym="es",
    slug="spanish",
    image_filename="spain",
    flag_filename="es"
)

en = Language(
    english_name="English",
    original_name=u"English",
    acronym="en",
    slug="english",
    image_filename="uk",
    flag_filename="uk"
)

it = Language(
    english_name="Italian",
    original_name=u"Italiano",
    acronym="it",
    slug="italian",
    image_filename="italy",
    flag_filename="it"
)

de = Language(
    english_name="German",
    original_name=u"Deutsch",
    acronym="de",
    slug="german",
    image_filename="germany",
    flag_filename="de"
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
