# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-15 20:04
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20160315_2002'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='dataset',
            unique_together=set([('slug', 'pair')]),
        ),
    ]
