# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduled_classes', '0003_auto_20160516_1753'),
        ('users', '0003_auto_20160520_2115'),
        ('notifications', '0001_initial'),
        ('reports', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivitySession',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('reports.sessionsummary', models.Model),
        ),
        migrations.CreateModel(
            name='NewUser',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('users.user', models.Model),
        ),
        migrations.CreateModel(
            name='NotificationSent',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('notifications.notification', models.Model),
        ),
        migrations.CreateModel(
            name='SessionCancelled',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('scheduled_classes.class', models.Model),
        ),
        migrations.CreateModel(
            name='SessionRegistered',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('scheduled_classes.class', models.Model),
        ),
        migrations.CreateModel(
            name='TopUser',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('users.user', models.Model),
        ),
    ]
