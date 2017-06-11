# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('promotions', '0002_auto_20160510_1823'),
        ('scheduled_classes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='class',
            name='promo_code',
            field=models.OneToOneField(related_name='session', null=True, blank=True, to='promotions.PromotionCode', verbose_name=b'promotion code'),
        ),
    ]
