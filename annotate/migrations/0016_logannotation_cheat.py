# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-12 11:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annotate', '0015_logannotation_logranking'),
    ]

    operations = [
        migrations.AddField(
            model_name='logannotation',
            name='cheat',
            field=models.BooleanField(default=False),
        ),
    ]