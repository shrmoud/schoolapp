# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20160520_2115'),
        ('reports', '0003_sessionsale'),
    ]

    operations = [
        migrations.DeleteModel(
            name='TopUser',
        ),
        migrations.CreateModel(
            name='TopStudentUser',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('users.user', models.Model),
        ),
        migrations.CreateModel(
            name='TopTeacherUser',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('users.user', models.Model),
        ),
    ]
