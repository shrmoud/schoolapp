# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduled_classes', '0011_auto_20160804_1801'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classbill',
            name='promo_code',
            field=models.ForeignKey(related_name='class_bills', verbose_name=b'promotion code', blank=True, to='promotions.PromotionCode', null=True),
        ),
    ]
