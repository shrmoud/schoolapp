# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduled_classes', '0007_auto_20160525_2013'),
    ]

    operations = [
        migrations.AddField(
            model_name='classbill',
            name='charge_id',
            field=models.CharField(max_length=100, null=True, verbose_name=b'charge id', blank=True),
        ),
    ]
