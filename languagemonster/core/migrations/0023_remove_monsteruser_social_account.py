# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-08-25 18:49
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_auto_20160820_0932'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='monsteruser',
            name='social_account',
        ),
    ]