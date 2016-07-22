import uuid
import factory
from factory.fuzzy import (
    FuzzyAttribute,
    FuzzyText,
)

from core.models import (
    Language,
    BaseLanguage,
    LanguagePair,
    WordPair,
    UserWordPair,
    MonsterUser,
    MonsterUserGame,
    Progression,
    DataSet,
    DS2WP,
    UserResult,
)

from django.contrib.auth import models as contrib_models

from utility.testing import get_random_unicode

class WordPairFactory(factory.Factory):
    class Meta:
        model = WordPair

    base = FuzzyAttribute(get_random_unicode)
    target = FuzzyAttribute(get_random_unicode)


class LanguageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Language

    english_name = FuzzyText()
    original_name = FuzzyText()
    acronym = FuzzyText(length=2)
    slug = FuzzyText()

class BaseLanguageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BaseLanguage

    language = factory.SubFactory(LanguageFactory)
    original_name = FuzzyText()
    country = FuzzyText(length=2)


class LanguagePairFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LanguagePair

    base_language = factory.SubFactory(Language)
    target_language = factory.SubFactory(Language)

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = contrib_models.User

    username = factory.Sequence(lambda n: 'user%s' % n)
    first_name = FuzzyText()


class MonsterUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MonsterUser

    user = factory.SubFactory(UserFactory)
    current_language = factory.SubFactory(LanguageFactory)
    base_language = factory.SubFactory(BaseLanguageFactory)
    public_name = FuzzyText()
    uri = factory.Sequence(lambda n: 'uri%s' % n)
    api_login_hash = FuzzyAttribute(uuid.uuid4)
    secure_hash = FuzzyAttribute(uuid.uuid4)

class UserWordPairFactory(factory.Factory):
    class Meta:
        model = UserWordPair

    word_pair = factory.SubFactory(WordPair)
    user = factory.SubFactory(MonsterUserFactory)

class MonsterUserGameFactory(factory.Factory):
    class Meta:
        model = MonsterUserGame

    monster_user = factory.SubFactory(MonsterUserFactory)
    game = FuzzyText()

class ProgressionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Progression

    user = factory.SubFactory(Progression)
    pair = factory.SubFactory(LanguagePair)

class DataSetFactory(factory.Factory):
    class Meta:
        model = DataSet

    pair = factory.SubFactory(LanguagePairFactory)

class DS2WPFactory(factory.Factory):
    class Meta:
        model = DS2WP

    ds = factory.SubFactory(DataSetFactory)
    wp = factory.SubFactory(WordPairFactory)

class UserResultFactory(factory.Factory):
    class Meta:
        model = UserResult

    user = factory.SubFactory(MonsterUserFactory)
    data_set = factory.SubFactory(DataSetFactory)