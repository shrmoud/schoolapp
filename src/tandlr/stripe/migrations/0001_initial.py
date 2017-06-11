# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('scheduled_classes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StripeCard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('card_id', models.CharField(max_length=255, null=True, verbose_name='stripe id', blank=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created at')),
                ('name', models.TextField(null=True, verbose_name='name', blank=True)),
                ('address_line_1', models.TextField(null=True, verbose_name='address line 1', blank=True)),
                ('address_line_1_check', models.CharField(max_length=15, null=True, verbose_name='address line 1 check', blank=True)),
                ('address_line_2', models.TextField(null=True, verbose_name='address line 2', blank=True)),
                ('address_city', models.TextField(null=True, verbose_name='address city', blank=True)),
                ('address_state', models.TextField(null=True, verbose_name='address state', blank=True)),
                ('address_country', models.TextField(null=True, verbose_name='address country', blank=True)),
                ('address_zip', models.TextField(null=True, verbose_name='address zip', blank=True)),
                ('address_zip_check', models.CharField(max_length=15, null=True, verbose_name='address zip check')),
                ('brand', models.TextField(null=True, verbose_name='brand', blank=True)),
                ('country', models.CharField(max_length=2, null=True, verbose_name='country', blank=True)),
                ('cvc_check', models.CharField(max_length=15, null=True, verbose_name='cvc check', blank=True)),
                ('dynamic_last4', models.CharField(max_length=4, null=True, verbose_name='dynamic last 4 digits', blank=True)),
                ('is_default', models.BooleanField(default=False, verbose_name='default card')),
                ('tokenization_method', models.CharField(max_length=15, null=True, verbose_name='tokenization method', blank=True)),
                ('exp_month', models.IntegerField(verbose_name='expiration month')),
                ('exp_year', models.IntegerField(verbose_name='expiration year')),
                ('funding', models.CharField(max_length=15, null=True, verbose_name='funding', blank=True)),
                ('last4', models.CharField(max_length=4, null=True, verbose_name='last 4 digits', blank=True)),
                ('fingerprint', models.TextField(null=True, verbose_name='fingerprint', blank=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='is active')),
            ],
        ),
        migrations.CreateModel(
            name='StripeCharge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('charge_id', models.CharField(unique=True, max_length=255, verbose_name='stripe id')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created at')),
                ('currency', models.CharField(default=b'usd', max_length=10, verbose_name='currency')),
                ('amount', models.DecimalField(null=True, verbose_name='amount', max_digits=9, decimal_places=2)),
                ('amount_refunded', models.DecimalField(null=True, verbose_name='amount refunded', max_digits=9, decimal_places=2)),
                ('description', models.TextField(verbose_name='description', blank=True)),
                ('paid', models.NullBooleanField(verbose_name='paid')),
                ('disputed', models.NullBooleanField(verbose_name='disputed')),
                ('refunded', models.NullBooleanField(verbose_name='refunded')),
                ('captured', models.NullBooleanField(verbose_name='captured')),
                ('charge_created', models.DateTimeField(null=True, verbose_name='charge created', blank=True)),
                ('card', models.ForeignKey(related_name='charges', on_delete=django.db.models.deletion.SET_NULL, verbose_name='card', blank=True, to='stripe.StripeCard', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='StripeCustomer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('customer_id', models.CharField(max_length=255, verbose_name='stripe id', blank=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created at')),
                ('account_balance', models.DecimalField(null=True, verbose_name='account balance', max_digits=9, decimal_places=2)),
                ('currency', models.CharField(default=b'usd', max_length=10, verbose_name='currency')),
                ('delinquent', models.BooleanField(default=False, verbose_name='deliquent')),
                ('default_source', models.TextField(verbose_name='default source', blank=True)),
                ('date_purged', models.DateTimeField(verbose_name='date purged', null=True, editable=False)),
                ('user', models.OneToOneField(null=True, verbose_name='user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='stripecharge',
            name='customer',
            field=models.ForeignKey(related_name='charges', verbose_name='customer', to='stripe.StripeCustomer'),
        ),
        migrations.AddField(
            model_name='stripecharge',
            name='related_class',
            field=models.ForeignKey(related_name='payments', verbose_name='related class', to='scheduled_classes.Class'),
        ),
        migrations.AddField(
            model_name='stripecard',
            name='customer',
            field=models.ForeignKey(verbose_name='customer', to='stripe.StripeCustomer'),
        ),
    ]
