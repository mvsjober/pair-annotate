# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-23 14:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annotate', '0004_auto_20160216_1427'),
    ]

    operations = [
        migrations.AddField(
            model_name='shotpair',
            name='annotation',
            field=models.SmallIntegerField(default=0),
        ),
    ]
