# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20160511_1802'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersummary',
            name='lessons_as_student',
            field=models.PositiveIntegerField(default=0, help_text='Defines how much lessons the user has taken as student', verbose_name='lessons as student'),
        ),
        migrations.AddField(
            model_name='usersummary',
            name='sessions_as_teacher',
            field=models.PositiveIntegerField(default=0, help_text='Defines how much sessions the user has taken as teacher', verbose_name='sessions as teacher'),
        ),
    ]
