# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-06-18 02:01
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.postgres.fields.hstore
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('hs_core', '0050_auto_20200611_1912'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LDAWord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.CharField(choices=[('ODM2', 'ODM2'), ('CSDMS', 'CSDMS'), ('Customized', 'Customized')], max_length=10)),
                ('word_type', models.CharField(choices=[('keep', 'keep'), ('stop', 'stop')], max_length=4)),
                ('part', models.CharField(choices=[('name', 'name'), ('decor', 'decor')], max_length=5)),
                ('value', models.CharField(editable=False, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='RecommendedResource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('relevance', models.FloatField(default=0.0, editable=False)),
                ('rec_type', models.CharField(choices=[('Ownership', 'Ownership'), ('Propensity', 'Propensity'), ('Combination', 'Combination')], max_length=11, null=True)),
                ('state', models.IntegerField(choices=[(1, 'New'), (2, 'Shown'), (3, 'Explored'), (4, 'Approved'), (5, 'Dismissed')], default=1, editable=False)),
                ('keywords', django.contrib.postgres.fields.hstore.HStoreField(default={})),
                ('candidate_resource', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='resource_recommendation_test', to='hs_core.BaseResource')),
                ('user', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserPreferences',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('preferences', django.contrib.postgres.fields.hstore.HStoreField(default={})),
                ('pref_for', models.CharField(choices=[('Resource', 'Resource'), ('User', 'User'), ('Group', 'Group')], max_length=8)),
                ('user', models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='recommendedresource',
            unique_together=set([('user', 'candidate_resource', 'rec_type')]),
        ),
    ]
