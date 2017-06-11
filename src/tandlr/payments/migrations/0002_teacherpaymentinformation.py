# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeacherPaymentInformation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('bank', models.CharField(max_length=255, verbose_name=b'bank')),
                ('account_number', models.CharField(max_length=255, verbose_name=b'account number')),
                ('social_security_number', models.CharField(max_length=255, verbose_name=b'social security number')),
                ('teacher', models.OneToOneField(verbose_name=b'teacher', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
