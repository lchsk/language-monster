# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-09-26 21:30
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_auto_20160917_1702'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='baselanguage',
            name='language',
        ),
        migrations.AlterUniqueTogether(
            name='languagepair',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='languagepair',
            name='base_language',
        ),
        migrations.RemoveField(
            model_name='languagepair',
            name='target_language',
        ),
        migrations.DeleteModel(
            name='BaseLanguage',
        ),
        migrations.DeleteModel(
            name='Language',
        ),
        migrations.DeleteModel(
            name='LanguagePair',
        ),
    ]