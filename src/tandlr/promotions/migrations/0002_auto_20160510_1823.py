# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('promotions', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='promotioncodeuser',
            name='promotion_code',
        ),
        migrations.RemoveField(
            model_name='promotioncodeuser',
            name='user',
        ),
        migrations.RenameField(
            model_name='promotioncode',
            old_name='status',
            new_name='is_active',
        ),
        migrations.AddField(
            model_name='promotioncode',
            name='discount',
            field=models.DecimalField(default=Decimal('0.00'), max_digits=6, decimal_places=2),
        ),
        migrations.AddField(
            model_name='promotioncode',
            name='spent_date',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='promotioncode',
            name='was_spent',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='promotioncode',
            name='code',
            field=models.CharField(max_length=31, unique=True, null=True, blank=True),
        ),
        migrations.DeleteModel(
            name='PromotionCodeUser',
        ),
    ]
