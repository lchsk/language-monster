# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-05-01 12:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_auto_20160501_0045'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monsteruser',
            name='current_language',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='monster_user_current_language', to='core.Language'),
        ),
    ]
