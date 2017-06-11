# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('promotions', '0002_auto_20160510_1823'),
    ]

    operations = [
        migrations.CreateModel(
            name='BatchPromotionCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.IntegerField()),
                ('expiration_date', models.DateTimeField()),
                ('discount', models.DecimalField(default=Decimal('0.00'), max_digits=6, decimal_places=2)),
            ],
        ),
    ]
