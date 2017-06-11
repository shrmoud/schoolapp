# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20160822_1928'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='gender',
            field=models.IntegerField(blank=True, null=True, choices=[(1, b'Female'), (2, b'Male'), (3, b"Don't Specify")]),
        ),
        migrations.AlterField(
            model_name='user',
            name='university',
            field=models.ForeignKey(blank=True, to='catalogues.University', null=True),
        ),
    ]
