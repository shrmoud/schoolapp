# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20160520_2115'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersummary',
            name='score_average_student',
            field=models.FloatField(default=5.0, null=True, verbose_name='student rate'),
        ),
        migrations.AlterField(
            model_name='usersummary',
            name='score_average_teacher',
            field=models.FloatField(default=5.0, null=True, verbose_name='teacher rate'),
        ),
    ]
