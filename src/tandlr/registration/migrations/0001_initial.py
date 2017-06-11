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
            name='RegistrationProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='created date', null=True)),
                ('last_modified', models.DateTimeField(auto_now=True, verbose_name='last modified', null=True)),
                ('activation_key', models.CharField(unique=True, max_length=40, verbose_name='activation key')),
                ('is_activated', models.BooleanField(default=False, verbose_name='is activated')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Registration Profile',
                'verbose_name_plural': 'Registration Profiles',
            },
        ),
        migrations.CreateModel(
            name='ResetPassword',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='created date', null=True)),
                ('last_modified', models.DateTimeField(auto_now=True, verbose_name='last modified', null=True)),
                ('activation_key', models.CharField(unique=True, max_length=40, verbose_name='activation key')),
                ('is_activated', models.BooleanField(default=False, verbose_name='is activated')),
                ('user', models.ForeignKey(related_name='reset_password', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Reset Password',
                'verbose_name_plural': 'Reset Passwords',
            },
        ),
    ]
