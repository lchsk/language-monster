
from django.utils.text import slugify
from django.db import models
from django.contrib.auth import models as contrib_models

from core.data.language_pair import (
    LANGUAGE_PAIRS_FLAT,
    LANGUAGE_PAIRS_FLAT_ALL,
)

from core.data.base_language import BASE_LANGUAGES

class Language(models.Model):

    # Name of the language in English
    english_name = models.CharField(
        max_length=25,
        # null=True,
        unique=True
    )

    # Name of language in native language: English, polski, italiano, espanol
    original_name = models.CharField(
        max_length=25,
        unique=True
        # null=True
    )

    # Two-letter acronym of the language, eg. en, pl, es, de
    acronym = models.CharField(
        max_length=5,
        unique=True,
        # null=True
    )

    slug = models.CharField(
        max_length=20,
        unique=True,
        # null=True
    )

    # /static/images/countries/
    image_filename = models.CharField(
        max_length=30,
        # null=True
    )

    # /static/images/flags/
    flag_filename = models.CharField(
        max_length=10,
        # null=True
    )

    class Meta:
        verbose_name = 'Language'
        verbose_name_plural = 'Languages'

    def __unicode__(self):
        return u'{english} ({acronym} / {slug})'.format(
            english=self.english_name,
            acronym=self.acronym,
            slug=self.slug
        )


class LanguagePair(models.Model):

    base_language = models.ForeignKey(
        Language,
        on_delete=models.CASCADE,
        related_name='base_language',
        db_index=True
    )

    target_language = models.ForeignKey(
        Language,
        on_delete=models.CASCADE,
        related_name='target_language',
        db_index=True
    )

    visible = models.BooleanField(
        default=True
    )

    learners = models.IntegerField(
        default=0,
        help_text='Number of people learning'
    )

    class Meta:
        unique_together = ('base_language', 'target_language')
        verbose_name = 'Language Pair'
        verbose_name_plural = 'Language Pairs'

    def __unicode__(self):
        return u'{base} -> {target}'.format(
            base=self.base_language.english_name,
            target=self.target_language.english_name
        )


class BaseLanguage(models.Model):

    flag_filename = models.CharField(max_length=10)

    original_name = models.CharField(
        max_length=25,
        unique=True
    )

    # Country acronym
    country = models.CharField(
        max_length=2,
        unique=True
    )

    language = models.ForeignKey(
        Language,
        on_delete=models.CASCADE,
        related_name='language',
        db_index=True,
    )
    # language = models.OneToOneField(
    #     Language,
    #     db_index=True,
    #     unique=False
    # )

    visible = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'BaseLanguage'
        verbose_name_plural = 'Base Languages'

    def __unicode__(self):
        return u'{language}: {original_name}'.format(
            language=self.language,
            original_name=self.original_name
        )


class MonsterUser(models.Model):
    user = models.OneToOneField(
        contrib_models.User,
        db_index=True,
        unique=True
    )

    public_name = models.CharField(max_length=30)
    new_email = models.CharField(max_length=50)
    secure_hash = models.CharField(max_length=250, unique=True, null=True)
    api_login_hash = models.CharField(max_length=250, unique=True)
    avatar = models.CharField(max_length=250)

    # base language
    language = models.CharField(
        max_length=5,
        null=False,
        default='en_uk',
        help_text='Base Language',
        choices=sorted([
            (symbol, lang.original_name)
            for symbol, lang in BASE_LANGUAGES.items()
        ])
    )
    
    # Base language of the current user: used for interface,
    # as well as base for learning. Can be changed by the user at any time.
    # current_language = models.ForeignKey(
    #     Language,
    #     on_delete=models.CASCADE,
    #     related_name='monster_user_current_language',
    #     db_index=True,
    #     null=True,
    # )

    # Helps with differentiating between US/UK English etc.

    # base_language = models.ForeignKey(
    #     BaseLanguage,
    #     on_delete=models.CASCADE,
    #     related_name='monster_user_base_language',
    #     # TODO: that should be removed at some point
    #     null=True,
    # )

    # Number of data sets user is learning (in all languages)
    datasets = models.IntegerField(default=0)

    # User's chosen address: /profile/uri
    uri = models.CharField(
        max_length=150,
        db_index=True,
        unique=True
    )

    birthday = models.DateTimeField(null=True)

    social_account = models.BooleanField(default=False)

    gender = models.CharField(
        max_length=2,
        null=True,
        choices=(
            ('M', 'Male'),
            ('F', 'Female'),
        )
    )

    # City...
    location = models.CharField(
        default='',
        max_length=18,
        null=True
    )

    country = models.CharField(default='', max_length=20)

    www = models.CharField(default='', max_length=20)

    # 'About me' message
    about = models.CharField(default='', max_length=500)

    # meta = {
    #     'indexes': [
    #         {'fields': ['email'], 'unique': True, 'sparse': True, 'types': False },
    #         {'fields': ['uri'], 'unique': True, 'sparse': True, 'types': False },
    #     ],
    # }

    class Meta:
        verbose_name = 'MonsterUser'
        verbose_name_plural = 'Monster Users'

    def __unicode__(self):
        return u'{email}'.format(
            email=self.user.email,
        )

class MonsterUserGame(models.Model):
    monster_user = models.ForeignKey(
        MonsterUser,
        related_name='monster_user_game',
        db_index=True
    )
    game = models.CharField(default='', max_length=20)

    played = models.BooleanField(default=False)
    banned = models.BooleanField(default=False)
    # TODO: choices
    # status = models.CharField(default='', max_length=1)

    class Meta:
        verbose_name = 'MonsterUserGame'
        verbose_name_plural = 'Monster User Games'

    def __unicode__(self):
        return u'{user}: {game}'.format(
            user=self.monster_user,
            game=self.game
        )


class DataSet(models.Model):

    # Filename of the file with vocabulary data
    # filename = StringField(required=False, max_length=50, help_text='Dataset filename')

    # Name of the dataset eg. Animals, Countries
    name_en = models.CharField(
        max_length=50,
        help_text='Name in English',
        unique=False
    )
    name_base = models.CharField(
        max_length=50,
        help_text='Name in base language',
        unique=False
    )
    name_target = models.CharField(
        max_length=50,
        help_text='Name in target language',
        unique=False
    )

    slug = models.CharField(
        max_length=50,
        help_text='URL slug',
        db_index=True,
        unique=False
    )

    icon = models.CharField(
        max_length=50,
        help_text='Icon filename'
    )

    date_added = models.DateTimeField(
        auto_now_add=True,
        help_text='Date added'
    )

    visible = models.BooleanField(default=False)
    from_exported_file = models.BooleanField(
        default=False,
        help_text='Data set was generated from an exported file'
    )

    # Number of words in this dataset
    word_count = models.IntegerField(
        help_text='Number of words in the dataset'
    )

    pos = models.CharField(max_length=20, help_text='Part of Speech')

    # pair = ReferenceField(LanguagePair, help_text='Base and target language')
    # pair = models.ForeignKey(
    #     LanguagePair,
    #     related_name='dataset_pair',
    #     db_index=True
    # )

    lang_pair = models.CharField(
        max_length=5,
        null=False,
        default='en_en',
        help_text='Language Pair',
        choices=sorted([
            (symbol, '{b} -> {t}'.format(
                b=pair.base_language.english_name,
                t=pair.target_language.english_name
            ))
            for symbol, pair in LANGUAGE_PAIRS_FLAT_ALL.items()
        ])
    )

    # List of tags that describe this dataset
    # tags = ListField(StringField(max_length=30), help_text='List of tags')

    learners = models.IntegerField(
        default=0,
        help_text='Number of people learning this dataset'
    )

    simple_dataset = models.BooleanField(
        default=False,
        help_text='If true, then this dataset is '
        'designed to contain basic words only'
    )

    # true if this set was created by reversing already existing set
    reversed_set = models.BooleanField(default=False)

    # meta = {
    #     'indexes': [
    #         {'fields': ['slug'] },
    #         {'fields': ['pair'] },
    #     ],
    # }

    class Meta:
        unique_together = ('slug', 'lang_pair')
        verbose_name = 'DataSet'
        verbose_name_plural = 'Data Sets'

    def __unicode__(self):
        return u'{0} [{1}]'.format(
            self.name_en,
            self.lang_pair
        )

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name_en)
        super(DataSet, self).save(*args, **kwargs)


class DataSetProgress(models.Model):

    date_set = models.ForeignKey(
        DataSet,
        related_name='data_set_progress',
        db_index=True
    )
    user = models.ForeignKey(
        MonsterUser,
        related_name='data_set_user',
        db_index=True
    )

    strength = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'DataSetProgress'
        verbose_name_plural = 'Data Set Progress'

    def __unicode__(self):
        return u'{0}: {1}'.format(self.user, self.data_set)

    # meta = {
    #     'indexes': [
    #         {'fields': ['data_set'] },
    #         {'fields': ['user'] },
    #         {'fields': ['data_set', 'user'] },
    #     ],
    # }


class WordPair(models.Model):

    # Word in Base Language
    base = models.TextField()

    # Word in Target Language
    target = models.TextField()

    # Mostly for adding/editing new data set

    # Word in English
    english = models.TextField()

    # Full, unparsed
    comments = models.TextField()

    # Part of Speech (in English, eg. Noun)

    pos = models.TextField()

    base_en = models.TextField()
    target_en = models.TextField()
    english_invalid = models.BooleanField(default=False)
    from_english = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)

    ################################################
    # That will have to be deleted at some point
    ################################################
    # data_set = ReferenceField(DataSet)
    # data_set = models.ForeignKey(
    #     DataSet,
    #     null=True,
    #     related_name='word_pair_data_set'
    # )

    index = models.IntegerField(default=0)

    pop = models.IntegerField(default=0, help_text='Popularity')

    # meta = {
    #     'indexes': [
    #         {'fields': ['base'] },
    #         {'fields': ['target'] },
    #         {'fields': ['base', 'target'] },
    #     ],
    # }

    class Meta:
        verbose_name = 'WordPair'
        verbose_name_plural = 'Word Pairs'

    def __unicode__(self):
        return u'{base} = {target}'.format(
            base=self.base,
            target=self.target
        )


class Progression(models.Model):
    '''
    Holds information about the progress a particular user has made
    for a particular Language.
    '''

    user = models.ForeignKey(
        MonsterUser,
        related_name='progression_monster_user',
        db_index=True
    )

    # pair = models.ForeignKey(
    #     LanguagePair,
    #     related_name='progression_pair',
    #     db_index=True,
    #     null=True,
    # )

    lang_pair = models.CharField(
        max_length=5,
        null=False,
        default='en_en',
        help_text='Language Pair',
        choices=sorted([
            (symbol, '{b} -> {t}'.format(
                b=pair.base_language.english_name,
                t=pair.target_language.english_name
            ))
            for symbol, pair in LANGUAGE_PAIRS_FLAT.items()
        ])
    )

    # How many words a user knows
    words = models.IntegerField(default=0)

    # Number of days when user completed a level
    streak = models.IntegerField(default=0)

    # [points]
    strength = models.IntegerField(default=0)

    # Indicated whether strengh is up or dowolnego
    # 1 - up, 0 - no change, -1 - down
    trend = models.IntegerField(default=0)

    # Average of all results
    average = models.IntegerField(default=0)

    # Number of datasets user is learning in this language
    datasets = models.IntegerField(default=0)

    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'lang_pair')
        verbose_name = 'Progression'
        verbose_name_plural = 'Progressions'

    def __unicode__(self):
        return u'{user}: {lang_pair}'.format(
            user=self.user,
            lang_pair=self.lang_pair
        )

    # meta = {
    #     'indexes': [
    #         {'fields': ['pair'] },
    #         {'fields': ['user'] },
    #         {'fields': ['pair', 'user'] },
    #     ],
    # }


class UserWordPair(models.Model):

    word_pair = models.ForeignKey(
        WordPair,
        related_name='user_word_pair_word_pair',
        db_index=True
    )
    user = models.ForeignKey(
        MonsterUser,
        related_name='user_word_pair_user',
        db_index=True
    )
    repeat = models.BooleanField(default=False)
    learned = models.BooleanField(default=False)

    class Meta:
        unique_together = ('word_pair', 'user')
        verbose_name = 'UserWordPair'
        verbose_name_plural = 'User Word Pairs'

    # meta = {
    #     'indexes': [
    #         {'fields': ['word_pair'] },
    #         {'fields': ['user'] },
    #     ],
    # }

    def __unicode__(self):
        return u'{word_pair}: {user}'.format(
            word_pair=self.word_pair,
            user=self.user
        )


class UserResult(models.Model):

    user = models.ForeignKey(
        MonsterUser,
        related_name='user_result_user',
        db_index=True
    )
    data_set = models.ForeignKey(
        DataSet,
        related_name='user_result_data_set',
        db_index=True
    )
    date = models.DateTimeField(auto_now_add=True)
    mark = models.IntegerField(default=0)
    game = models.CharField(max_length=30)

    class Meta:
        # unique_together = ('data_set', 'user')
        verbose_name = 'UserResult'
        verbose_name_plural = 'User Results'

    # meta = {
    #     'indexes': [
    #         {'fields': ['data_set'] },
    #         {'fields': ['user'] },
    #     ],
    # }


class ErrorReport(models.Model):
    '''Reports people send'''

    user = models.ForeignKey(
        MonsterUser,
        related_name='error_report_user',
        null=True
    )
    date = models.DateTimeField(
        auto_now_add=True
    )
    text = models.CharField(max_length=256)
    data_set = models.ForeignKey(
        DataSet,
        related_name='error_report_data_set',
        null=True
    )

    class Meta:
        verbose_name = 'ErrorReport'
        verbose_name_plural = 'Error Reports'


class MobileDevice(models.Model):
    """
        All devices registered with the API
    """

    # User account linked to the device

    user = models.ForeignKey(
        MonsterUser,
        related_name='mobile_device_user',
        null=True,
        db_index=True
    )

    # Time of device registration

    date = models.DateTimeField(auto_now_add=True)

    # Operating system

    os = models.CharField(max_length=100, null=True)

    device_key = models.CharField(null=False, max_length=255)

    ip = models.CharField(max_length=100, null=True)

    # Name of the device

    device = models.CharField(max_length=100, null=True)

    display = models.CharField(max_length=100, null=True)

    hardware = models.CharField(max_length=100, null=True)

    manufacturer = models.CharField(max_length=100, null=True)

    model = models.CharField(max_length=100, null=True)

    # SDK version

    sdk = models.CharField(max_length=100, null=True)

    # OS language

    language = models.CharField(max_length=100, null=True)

    class Meta:
        verbose_name = 'MobileDevice'
        verbose_name_plural = 'Mobile Devices'

    # meta = {
    #     'indexes': [
    #         {'fields': ['user'] },
    #     ],
    # }


class SimpleDataset(models.Model):
    """
        A dataset used to generate simple (shortened) datasets from full ones
    """

    date = models.DateTimeField(auto_now_add=True)

    name = models.CharField(max_length=100, unique=True)
    data = models.TextField(null=True)

    class Meta:
        verbose_name = 'SimpleDataset'
        verbose_name_plural = 'Simple Datasets'


class DS2WP(models.Model):
    """
        DataSet to WordPair mapping
    """

    ds = models.ForeignKey(
        DataSet,
        related_name='ds2wp_ds',
        db_index=True
    )
    wp = models.ForeignKey(
        WordPair,
        related_name='ds2wp_wp',
        db_index=True
    )

    class Meta:
        unique_together = ('ds', 'wp')
        verbose_name = 'DS2WP'
        verbose_name_plural = 'DataSet to WordPair'

    # meta = {
    #     'indexes': [
    #         {'fields': ['ds'] },
    #         {'fields': ['wp'] },
    #         {'fields': ['ds', 'wp'] },
    #     ],
    # }


class OpenGameSession(models.Model):
    """
    """

    date = models.DateTimeField(auto_now_add=True)
    game_session_id = models.CharField(
        max_length=128,
        db_index=True,
        unique=True
    )
    game_token = models.CharField(
        max_length=128,
        unique=True
    )
    user = models.ForeignKey(
        MonsterUser,
        related_name='open_game_session_user'
    )
    dataset = models.ForeignKey(
        DataSet,
        related_name='open_game_session_dataset',
        db_index=True
    )

    class Meta:
        verbose_name = 'OpenGameSession'
        verbose_name_plural = 'Open Game Sessions'
