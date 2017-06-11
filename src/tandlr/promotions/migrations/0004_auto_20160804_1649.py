# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('promotions', '0003_batchpromotioncode'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='promotioncode',
            name='spent_date',
        ),
        migrations.RemoveField(
            model_name='promotioncode',
            name='was_spent',
        ),
        migrations.AlterField(
            model_name='batchpromotioncode',
            name='expiration_date',
            field=models.DateTimeField(help_text='Time should be at least 15 minutes in the future.'),
        ),
    ]
