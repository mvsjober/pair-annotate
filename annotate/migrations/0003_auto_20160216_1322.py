# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-16 13:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('annotate', '0002_auto_20160211_1016'),
    ]

    operations = [
        migrations.AlterField(
            model_name='annotator',
            name='last_video',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='annotate.Video'),
        ),
    ]