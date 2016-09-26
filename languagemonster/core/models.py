
from django.utils.text import slugify
from django.db import models
from django.contrib.auth import models as contrib_models

from core.data.language_pair import (
    LANGUAGE_PAIRS_FLAT,
    LANGUAGE_PAIRS_FLAT_ALL,
)

from core.data.base_language import BASE_LANGUAGES

class MonsterUser(models.Model):
    user = models.OneToOneField(
        contrib_models.User,
        db_index=True,
        unique=True
    )

    public_name = models.CharField(max_length=30)
    new_email = models.CharField(max_length=50, null=True)
    secure_hash = models.CharField(
        max_length=250,
        unique=True,
        null=True,
    )
    api_login_hash = models.CharField(
        max_length=250,
        unique=True,
        db_index=True,
        null=True,
    )
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

    # Number of data sets user is learning (in all languages)
    datasets = models.IntegerField(default=0)

    # User's chosen address: /profile/uri
    uri = models.CharField(
        max_length=150,
        db_index=True,
        unique=True,
        null=False,
    )

    birthday = models.DateTimeField(null=True)

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

    class Meta:
        verbose_name = 'MonsterUserGame'
        verbose_name_plural = 'Monster User Games'

    def __unicode__(self):
        return u'{user}: {game}'.format(
            user=self.monster_user,
            game=self.game
        )


class DataSet(models.Model):
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

    status = models.CharField(
        max_length=1,
        null=False,
        default='A',
        help_text='Status of data set',
        choices=[('A', 'Active'), ('X', 'Deleted')],
    )

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

    index = models.IntegerField(default=0)

    pop = models.IntegerField(default=0, help_text='Popularity')

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
    in a particular Language.
    '''

    user = models.ForeignKey(
        MonsterUser,
        related_name='progression_monster_user',
        db_index=True
    )

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

    # Indicated whether strengh is up or down
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
        verbose_name = 'UserResult'
        verbose_name_plural = 'User Results'

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
