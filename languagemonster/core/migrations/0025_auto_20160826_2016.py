# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-08-26 20:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_auto_20160825_2021'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monsteruser',
            name='new_email',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
