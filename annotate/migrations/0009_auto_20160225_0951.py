# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-25 09:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annotate', '0008_auto_20160225_0833'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='p_values',
            field=models.TextField(default='', max_length=5000),
        ),
    ]
