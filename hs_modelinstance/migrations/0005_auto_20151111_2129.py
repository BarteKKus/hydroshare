# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hs_modelinstance', '0004_auto_20151110_1920'),
    ]

    operations = [
        migrations.AlterField(
            model_name='executedby',
            name='model_name',
            field=models.CharField(max_length=500, choices=[('-', '    ')]),
            preserve_default=True,
        ),
    ]
