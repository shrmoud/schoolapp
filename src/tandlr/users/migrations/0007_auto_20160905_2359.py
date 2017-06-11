# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20160822_1946'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersettings',
            name='available',
            field=models.BooleanField(default=False),
        ),
    ]
