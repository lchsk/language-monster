# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-15 20:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20160315_2004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataset',
            name='slug',
            field=models.CharField(db_index=True, help_text=b'URL slug', max_length=50),
        ),
    ]
