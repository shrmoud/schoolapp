# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountNumber',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('account_number', models.CharField(unique=True, max_length=16)),
                ('status', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'account_number',
            },
        ),
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('token', models.TextField(unique=True)),
                ('numbers_card', models.IntegerField()),
                ('status', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'card',
            },
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('symbol', models.CharField(unique=True, max_length=2)),
                ('code', models.CharField(unique=True, max_length=3)),
                ('status', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'currency',
                'verbose_name_plural': 'currencies',
            },
        ),
        migrations.CreateModel(
            name='PayerPayment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.DecimalField(max_digits=20, decimal_places=2)),
                ('payment_date', models.DateField(null=True)),
                ('status_payment', models.BooleanField(default=True)),
                ('user', models.ForeignKey(related_name='payer', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'payer_payment',
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.DecimalField(max_digits=20, decimal_places=2)),
                ('payment_date', models.DateField(null=True)),
                ('status_payment', models.BooleanField(default=True)),
                ('account_number', models.ForeignKey(to='payments.AccountNumber', null=True)),
                ('card', models.ForeignKey(to='payments.Card', null=True)),
                ('currency', models.ForeignKey(to='payments.Currency')),
            ],
            options={
                'db_table': 'payment',
            },
        ),
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=45)),
                ('description', models.CharField(max_length=100, null=True, blank=True)),
                ('status', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'payment_method',
            },
        ),
        migrations.CreateModel(
            name='StatusPayment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=45)),
                ('description', models.CharField(max_length=100, null=True, blank=True)),
                ('status', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'status_payment',
                'verbose_name': 'payment status',
                'verbose_name_plural': 'payment status',
            },
        ),
        migrations.CreateModel(
            name='TypeCard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=45)),
                ('description', models.CharField(max_length=100, null=True, blank=True)),
                ('status', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'type_card',
                'verbose_name': 'card type',
                'verbose_name_plural': 'card types',
            },
        ),
        migrations.CreateModel(
            name='TypePayment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=45)),
                ('description', models.CharField(max_length=100, null=True, blank=True)),
                ('status', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'type_payment',
                'verbose_name': 'payment type',
                'verbose_name_plural': 'payment types',
            },
        ),
        migrations.AddField(
            model_name='payment',
            name='payment_method',
            field=models.ForeignKey(to='payments.PaymentMethod'),
        ),
        migrations.AddField(
            model_name='payment',
            name='type_payment',
            field=models.ForeignKey(to='payments.TypePayment'),
        ),
        migrations.AddField(
            model_name='payment',
            name='user',
            field=models.ForeignKey(related_name='payment', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='card',
            name='type_card',
            field=models.ForeignKey(to='payments.TypeCard'),
        ),
        migrations.AddField(
            model_name='card',
            name='user',
            field=models.ForeignKey(related_name='card', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='accountnumber',
            name='type_card',
            field=models.ForeignKey(to='payments.TypeCard'),
        ),
        migrations.AddField(
            model_name='accountnumber',
            name='user',
            field=models.ForeignKey(related_name='account', to=settings.AUTH_USER_MODEL),
        ),
    ]
