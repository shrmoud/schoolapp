# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feedbacks', '0002_auto_20160705_2233'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedback',
            name='feedback_status',
            field=models.BooleanField(default=True),
        ),
    ]
