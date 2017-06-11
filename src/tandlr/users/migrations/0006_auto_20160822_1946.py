# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def initialize_sessions(apps, schema_editor):
    """
    Analyze the database registries. If the user has a zero in the
    field lessons_as_student or in the field sessions_as_teacher,
    change the number to 1
    """
    UserSummary = apps.get_model('users', 'UserSummary')

    UserSummary.objects.filter(
        lessons_as_student=0
    ).update(
        lessons_as_student=1
    )

    UserSummary.objects.filter(
        sessions_as_teacher=0
    ).update(
        sessions_as_teacher=1
    )


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20160824_1802'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersummary',
            name='lessons_as_student',
            field=models.PositiveIntegerField(default=1, help_text='Defines how much lessons the user has taken as student', verbose_name='lessons as student'),
        ),
        migrations.AlterField(
            model_name='usersummary',
            name='sessions_as_teacher',
            field=models.PositiveIntegerField(default=1, help_text='Defines how much sessions the user has taken as teacher', verbose_name='sessions as teacher'),
        ),
        migrations.RunPython(initialize_sessions)
    ]
