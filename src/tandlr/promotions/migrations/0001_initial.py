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
            name='PromotionCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('expiration_date', models.DateTimeField()),
                ('code', models.TextField(max_length=250, unique=True, null=True, blank=True)),
                ('status', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'promotion_code',
            },
        ),
        migrations.CreateModel(
            name='PromotionCodeUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('redemption_date', models.DateTimeField()),
                ('status', models.BooleanField(default=True)),
                ('promotion_code', models.ForeignKey(to='promotions.PromotionCode')),
                ('user', models.ForeignKey(related_name='promotions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'promotion_code_user',
            },
        ),
    ]
