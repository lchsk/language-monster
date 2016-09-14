from core.models import *
from rest_framework import serializers

from utility.api_utils import (
    CONST,
    fix_url,
)

############### NEW

class UserLoginRequest(serializers.Serializer):
    email = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=50)

class UserLoginResponse(serializers.Serializer):
    login_hash = serializers.CharField(
        max_length=128,
        allow_null=False,
        required=True,
    )

class LanguageSerializer(serializers.Serializer):
    english_name = serializers.CharField(max_length=30)
    original_name = serializers.CharField(max_length=30)
    acronym = serializers.CharField(max_length=2)
    slug = serializers.CharField(max_length=15)
    image_filename = serializers.CharField(max_length=20)
    flag_filename = serializers.CharField(max_length=20)

class BaseLanguageSerializer(serializers.Serializer):
    flag_filename = serializers.CharField(max_length=2)
    country = serializers.CharField(max_length=2)
    symbol = serializers.CharField(max_length=5)
    original_name = serializers.CharField(max_length=20)
    language = LanguageSerializer()

class LanguagePairSerializer(serializers.Serializer):
    base_language = LanguageSerializer()
    target_language = LanguageSerializer()
    symbol = serializers.CharField(max_length=5)

class DataSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSet
        fields = (
            'id',
            'learners',
            'name_base',
            'name_en',
            'name_target',
            'lang_pair',
            'word_count',
            'slug',
        )

################################################
#                                              #
#                    GetWords                  #
#                                              #
################################################

class GetWordsFilters(serializers.Serializer):
    rounds = serializers.IntegerField(default=10, min_value=1, max_value=30)
    sets = serializers.IntegerField(default=1, min_value=1, max_value=30)

class GetWordsSingleWordSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    words = serializers.ListField(
        child=serializers.CharField(min_length=1)
    )

class GetWordsSingleSetSerializer(serializers.Serializer):
    to_ask = serializers.ListField(child=GetWordsSingleWordSerializer())

################################################
#                                              #
#                UserProgression               #
#                                              #
################################################

class UserProgressionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Progression
        fields = (
            'average',
            'datasets',
            'lang_pair',
            'streak',
            'strength',
            'trend',
            'words',
        )

class StartLearningLanguageRequest(serializers.Serializer):
    lang_pair = serializers.CharField(max_length=5, min_length=5)


class UserRegistrationRequest(serializers.Serializer):
    email = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=50)
    base_language = serializers.CharField(max_length=5, min_length=5)
    # country = serializers.CharField(max_length=2, allow_null=True)
    # language = serializers.CharField(max_length=2, allow_null=True)


############### NEW

USER_FIELDS = (
    'public_name',
    'current_language',
    'base_language',
    'about',
    'avatar',
    'birthday',
    'country',
    'datasets',
    'gender',
    'location',
    'public_name',
    'uri',
    'www',
    'languages',

    'first_name',
    'last_name',
    'email',
    'is_active',

    'banned_games',
    'games_played',
)






# class LanguagePairSerializer(serializers.ModelSerializer):
#     base_language = LanguageSerializer()
#     target_language = LanguageSerializer()

#     class Meta:
#         model = LanguagePair
#         fields = ('base_language', 'learners', 'target_language')


class MonsterUserGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonsterUserGame
        fields = ('game',)



class BaseUserSerializer(serializers.ModelSerializer):
    current_language = LanguageSerializer()
    base_language = BaseLanguageSerializer()
    banned_games = MonsterUserGameSerializer(many=True)
    games_played = MonsterUserGameSerializer(many=True)
    languages = UserProgressionSerializer(many=True)
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.CharField(source='user.email')
    is_active = serializers.BooleanField(source='user.is_active')

    class Meta:
        model = MonsterUser
        fields = USER_FIELDS


class BaseUserSerializerWithLoginHash(BaseUserSerializer):
    class Meta:
        model = MonsterUser
        fields = USER_FIELDS + ('api_login_hash',)



class UserDetailsUpdateRequest(serializers.Serializer):
    first_name = serializers.CharField(
        max_length=50,
        allow_null=True,
        required=False
    )
    last_name = serializers.CharField(
        max_length=50,
        allow_null=True,
        required=False
    )
    country = serializers.CharField(
        max_length=2,
        allow_null=True,
        required=False
    )
    gender = serializers.CharField(
        max_length=1,
        allow_null=True,
        required=False
    )
    location = serializers.CharField(
        max_length=18,
        allow_null=True,
        required=False
    )
    uri = serializers.CharField(
        max_length=150,
        allow_null=True,
        required=False
    )
    www = serializers.CharField(
        max_length=20,
        allow_null=True,
        required=False
    )
    birthday = serializers.DateTimeField(
        allow_null=True,
        required=False
    )
    about = serializers.CharField(
        max_length=500,
        allow_null=True,
        required=False
    )



class ResultsSubmitRequest(serializers.Serializer):

    dataset_id = serializers.IntegerField()
    email = serializers.CharField(max_length=50, allow_null=False)
    mark = serializers.IntegerField()
    game = serializers.CharField(max_length=15, allow_null=False)
    words_learned = serializers.ListField(
        child=serializers.ListField(
            child=serializers.CharField(max_length=100)
        )
    )
    to_repeat = serializers.ListField(
        child=serializers.ListField(
            child=serializers.CharField(max_length=100)
        )
    )



def user_serializer_url(user):
    if CONST['USE_FULL_URLS']:
        if user:
            fix_url(user, 'avatar', 'AVATARS_DIR')

        if user and user.base_language:
            fix_url(user.base_language, 'flag_filename', 'FLAG_DIR')

        if user and user.base_language and user.base_language.language:
            fix_url(
                user.base_language.language,
                'image_filename',
                'COUNTRIES_DIR'
            )
            fix_url(user.base_language.language, 'flag_filename', 'FLAG_DIR')

        if user and user.current_language:
            fix_url(user.current_language, 'image_filename', 'COUNTRIES_DIR')
            fix_url(user.current_language, 'flag_filename', 'FLAG_DIR')


def language_pair_serializer_url(lp):
    if CONST['USE_FULL_URLS']:
        fix_url(lp.base_language, 'flag_filename', 'FLAG_DIR')
        fix_url(lp.base_language, 'image_filename', 'COUNTRIES_DIR')
        fix_url(lp.target_language, 'flag_filename', 'FLAG_DIR')
        fix_url(lp.target_language, 'image_filename', 'COUNTRIES_DIR')


def games_serializer_url(game):
    if CONST['USE_FULL_URLS']:
        fix_url(game, 'image', 'GAMES_IMAGES_DIR')
