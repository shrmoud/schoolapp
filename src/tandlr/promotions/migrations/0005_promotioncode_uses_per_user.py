# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('promotions', '0004_auto_20160804_1649'),
    ]

    operations = [
        migrations.AddField(
            model_name='promotioncode',
            name='uses_per_user',
            field=models.IntegerField(default=1, help_text='Defines the number of times a user can use the promo code.'),
        ),
    ]
