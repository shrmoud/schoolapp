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
            name='LogbookUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('activity', models.TextField(max_length=45, null=True, blank=True)),
                ('module', models.TextField(max_length=45, null=True, blank=True)),
                ('body_log', models.CharField(max_length=1000, null=True, blank=True)),
                ('log_level', models.CharField(default=b'INFO', max_length=5, choices=[(b'DEBUG', b'DEBUG'), (b'ERROR', b'ERROR'), (b'INFO', b'INFO')])),
                ('logbook_date', models.DateField(auto_now=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'logbook_user',
            },
        ),
        migrations.CreateModel(
            name='LogMail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mail_from', models.TextField(max_length=45)),
                ('mail_subject', models.TextField(max_length=50)),
                ('mail_sent_date', models.DateField(auto_now_add=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'log_mail',
            },
        ),
    ]
