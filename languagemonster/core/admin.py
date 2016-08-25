from django.contrib import admin

from .models import (
    MonsterUser,
    Language,
    LanguagePair,
    BaseLanguage,
    MonsterUserGame,
    DataSet,
    DataSetProgress,
    WordPair,
    Progression,
    UserWordPair,
    UserResult,
    MobileDevice,
    SimpleDataset,
    DS2WP,
    OpenGameSession,
)

tables = (
    # MonsterUser,
    Language,
    LanguagePair,
    BaseLanguage,
    MonsterUserGame,
    DataSet,
    DataSetProgress,
    WordPair,
    Progression,
    UserWordPair,
    UserResult,
    MobileDevice,
    SimpleDataset,
    DS2WP,
    OpenGameSession,
)

for table in tables:
    admin.site.register(table)

class MonsterUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'public_name', 'gender', 'language')

admin.site.register(MonsterUser, MonsterUserAdmin)
