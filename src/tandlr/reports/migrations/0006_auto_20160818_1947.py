# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0005_auto_20160525_1547'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sessioncancelled',
            options={'verbose_name': 'Session cancelled', 'verbose_name_plural': 'Sessions cancelled'},
        ),
    ]
