# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-08-28 18:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_auto_20160826_2016'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='status',
            field=models.CharField(choices=[(b'A', b'Active'), (b'X', b'Deleted')], default=b'A', help_text=b'Status of data set', max_length=1),
        ),
    ]
