# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('scheduled_classes', '0003_auto_20160516_1753'),
    ]

    operations = [
        migrations.AddField(
            model_name='class',
            name='participants',
            field=models.PositiveIntegerField(default=1, help_text='Defines the students number that will be in the session', validators=[django.core.validators.MinValueValidator(1)]),
            preserve_default=False,
        ),
    ]
