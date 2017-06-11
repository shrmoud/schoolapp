# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduled_classes', '0010_auto_20160715_1757'),
    ]

    operations = [
        migrations.AlterField(
            model_name='class',
            name='promo_code',
            field=models.ForeignKey(related_name='session', verbose_name=b'promotion code', blank=True, to='promotions.PromotionCode', null=True),
        ),
    ]
