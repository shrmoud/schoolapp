# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduled_classes', '0006_merge'),
        ('reports', '0002_activitysession_newuser_notificationsent_sessioncancelled_sessionregistered_topuser'),
    ]

    operations = [
        migrations.CreateModel(
            name='SessionSale',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('scheduled_classes.classbill', models.Model),
        ),
    ]
