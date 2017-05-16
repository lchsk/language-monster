from django.contrib import admin

from .models import (
    MonsterUser,
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
    Article,
)

tables = (
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
)

for table in tables:
    admin.site.register(table)

class MonsterUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'public_name', 'gender', 'language')

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'lang_pair', 'date')

admin.site.register(MonsterUser, MonsterUserAdmin)
admin.site.register(Article, ArticleAdmin)
