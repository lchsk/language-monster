from django.conf import settings

from rest_framework.serializers import (
    CharField,
    IntegerField,
    ListField,
    Serializer,
    ModelSerializer,
)

from core.models import (
    DataSet,
    Progression,
)

################################################
#                                              #
#                     User                     #
#                                              #
################################################

class UserLoginRequest(Serializer):
    email = CharField(max_length=50)
    password = CharField(max_length=50)

class UserLoginResponse(Serializer):
    login_hash = CharField(
        max_length=128,
        allow_null=False,
        required=True,
    )

################################################
#                                              #
#                     Data                     #
#                                              #
################################################

class LanguageSerializer(Serializer):
    english_name = CharField(max_length=30)
    original_name = CharField(max_length=30)
    acronym = CharField(max_length=2)
    slug = CharField(max_length=15)
    image_filename = CharField(max_length=20)
    flag_filename = CharField(max_length=20)

class BaseLanguageSerializer(Serializer):
    flag_filename = CharField(max_length=2)
    country = CharField(max_length=2)
    symbol = CharField(max_length=5)
    original_name = CharField(max_length=20)
    language = LanguageSerializer()

class LanguagePairSerializer(Serializer):
    base_language = LanguageSerializer()
    target_language = LanguageSerializer()
    symbol = CharField(max_length=5)

class DataSetSerializer(ModelSerializer):
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

class ToStudySerializer(Serializer):
    langs_to_learn = ListField(child=LanguagePairSerializer())
    datasets = ListField(child=DataSetSerializer())

################################################
#                                              #
#                    GetWords                  #
#                                              #
################################################

class GetWordsFilters(Serializer):
    rounds = IntegerField(
        default=settings.GAMES_DEFAULT_WORDS_COUNT,
        min_value=4,
        max_value=30,
    )
    sets = IntegerField(
        default=settings.GAMES_DEFAULT_WORD_SETS_COUNT,
        min_value=1,
        max_value=30,
    )

class GetWordsSingleWordSerializer(Serializer):
    id = IntegerField(required=True)
    words = ListField(child=CharField(min_length=1))

class GetWordsSingleSetSerializer(Serializer):
    to_ask = ListField(child=GetWordsSingleWordSerializer())

################################################
#                                              #
#                UserProgression               #
#                                              #
################################################

class UserProgressionSerializer(ModelSerializer):
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

class StartLearningLanguageRequest(Serializer):
    lang_pair = CharField(
        max_length=5,
        min_length=5,
        required=True,
    )

class UserRegistrationRequest(Serializer):
    email = CharField(max_length=50)
    password = CharField(max_length=50)
    base_language = CharField(max_length=5, min_length=5)

################################################
#                                              #
#                 Save Results                 #
#                                              #
################################################

class SaveResultsBase(Serializer):
    dataset_id = IntegerField()
    mark = IntegerField()
    game = CharField(max_length=15)
    words_learned = ListField(child=IntegerField())
    to_repeat = ListField(child=IntegerField())

# Called from a client
class SaveResultsRequest(SaveResultsBase):
    pass

# Called from JS
class SaveResultsJSRequest(SaveResultsBase):
    email = CharField(max_length=150)
