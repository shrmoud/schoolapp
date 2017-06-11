# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('scheduled_classes', '0003_auto_20160516_1753'),
    ]

    operations = [
        migrations.AddField(
            model_name='classbill',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name=b'Created date', auto_now_add=True),
            preserve_default=False,
        ),
    ]
