# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('promotions', '0002_auto_20160510_1823'),
        ('balances', '0001_initial'),
        ('scheduled_classes', '0002_class_promo_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClassBill',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hourly_price', models.DecimalField(default=Decimal('0.00'), verbose_name=b'hourly price', max_digits=6, decimal_places=2)),
                ('number_of_hours', models.TimeField(default=datetime.time(0, 0), verbose_name=b'number of hours')),
                ('subtotal', models.DecimalField(default=Decimal('0.00'), verbose_name=b'subtotal', max_digits=6, decimal_places=2)),
                ('commission', models.PositiveIntegerField(default=0, verbose_name=b'commission')),
                ('commission_amount', models.DecimalField(default=Decimal('0.00'), verbose_name=b'commission amount', max_digits=6, decimal_places=2)),
                ('was_paid', models.BooleanField(default=False, verbose_name=b'was paid')),
                ('balance', models.ForeignKey(related_name='bills', verbose_name=b'balance', blank=True, to='balances.Balance', null=True)),
                ('promo_code', models.OneToOneField(related_name='class_bills', null=True, blank=True, to='promotions.PromotionCode', verbose_name=b'promotion code')),
            ],
        ),
        migrations.AlterField(
            model_name='class',
            name='class_time',
            field=models.TimeField(default=datetime.time(0, 0)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='classbill',
            name='session',
            field=models.ForeignKey(related_name='bills', verbose_name=b'session', blank=True, to='scheduled_classes.Class', null=True),
        ),
    ]
