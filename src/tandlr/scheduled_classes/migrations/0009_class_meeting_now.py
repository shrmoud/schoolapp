# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduled_classes', '0008_classbill_charge_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='class',
            name='meeting_now',
            field=models.BooleanField(default=False, verbose_name=b'meeting now'),
        ),
    ]
