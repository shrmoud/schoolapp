# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduled_classes', '0009_class_meeting_now'),
    ]

    operations = [
        migrations.AddField(
            model_name='class',
            name='time_zone_conf',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='class',
            name='class_end_date',
            field=models.DateTimeField(default='2016-07-14 21:00:52.921276+00:00'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='class',
            name='class_start_date',
            field=models.DateTimeField(default='2016-07-14 20:00:52.921276+00:00'),
            preserve_default=False,
        ),
    ]
