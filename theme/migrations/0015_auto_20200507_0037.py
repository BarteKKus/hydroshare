# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-05-07 00:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('theme', '0014_comma_semicolon_delimiter'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userquota',
            name='unit',
            field=models.CharField(default='GB', max_length=10),
        ),
    ]