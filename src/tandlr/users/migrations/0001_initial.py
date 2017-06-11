# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields
import tandlr.users.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('catalogues', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(unique=True, max_length=50)),
                ('name', models.CharField(max_length=50, null=True, blank=True)),
                ('last_name', models.CharField(max_length=50, null=True, blank=True)),
                ('second_last_name', models.CharField(max_length=50, null=True, blank=True)),
                ('description', models.TextField(max_length=250, null=True, blank=True)),
                ('photo', models.ImageField(null=True, upload_to=tandlr.users.models.upload_to_image, blank=True)),
                ('thumbnail', models.ImageField(null=True, upload_to=tandlr.users.models.get_user_thumbnail_path, blank=True)),
                ('email', models.EmailField(unique=True, max_length=50)),
                ('phone', models.TextField(max_length=20, null=True, blank=True)),
                ('birthday', models.DateField(null=True)),
                ('gender', models.IntegerField(null=True, choices=[(1, b'Female'), (2, b'Male'), (3, b'Other')])),
                ('zip_code', models.CharField(max_length=10, null=True, blank=True)),
                ('register_date', models.DateField(auto_now=True)),
                ('last_modify_date', models.DateField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='is_active')),
                ('is_teacher', models.BooleanField(default=False, verbose_name='is_teacher')),
                ('is_student', models.BooleanField(default=True, verbose_name='is_student')),
                ('is_staff', models.BooleanField(default=False, verbose_name='is_staff')),
                ('is_confirmation_email', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'user',
            },
        ),
        migrations.CreateModel(
            name='DeviceUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='created date', null=True)),
                ('last_modified', models.DateTimeField(auto_now=True, verbose_name='last modified', null=True)),
                ('device_user_token', models.TextField(max_length=250, null=True, blank=True)),
                ('device_os', models.CharField(max_length=20)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'device_user',
            },
        ),
        migrations.CreateModel(
            name='LocationUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('point', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('last_modification_date', models.DateTimeField(auto_now_add=True)),
                ('place_description', models.TextField(max_length=250)),
            ],
            options={
                'db_table': 'location_user',
            },
        ),
        migrations.CreateModel(
            name='UserSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('session_confirm', models.BooleanField(default=True)),
                ('message', models.BooleanField(default=True)),
                ('session_cancellation', models.BooleanField(default=True)),
                ('location_change', models.BooleanField(default=True)),
                ('session_reminder', models.BooleanField(default=True)),
                ('available', models.BooleanField(default=True)),
                ('push_notifications_enabled', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'user_settings',
            },
        ),
        migrations.CreateModel(
            name='UserSummary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('score_average_teacher', models.FloatField(default=0.0, null=True, verbose_name='teacher rate')),
                ('score_average_student', models.FloatField(default=0.0, null=True, verbose_name='student rate')),
            ],
            options={
                'verbose_name': 'user summary',
                'verbose_name_plural': 'users summaries',
            },
        ),
        migrations.CreateModel(
            name='UserLogged',
            fields=[
                ('user', models.OneToOneField(related_name='logged', primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('last_login', models.DateField(auto_now_add=True)),
                ('number_login_attempt', models.IntegerField(null=True)),
                ('permissions_to_login', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'user_logged',
            },
        ),
        migrations.AddField(
            model_name='usersummary',
            name='user',
            field=models.OneToOneField(related_name='user_summary', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='usersettings',
            name='user',
            field=models.OneToOneField(related_name='settings', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='locationuser',
            name='user',
            field=models.OneToOneField(related_name='location_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='deviceuser',
            name='user',
            field=models.ForeignKey(related_name='devices', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='university',
            field=models.ForeignKey(to='catalogues.University', null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions'),
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
            ],
            options={
                'verbose_name': 'student',
                'proxy': True,
                'verbose_name_plural': 'students',
            },
            bases=('users.user',),
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
            ],
            options={
                'verbose_name': 'teacher',
                'proxy': True,
                'verbose_name_plural': 'teachers',
            },
            bases=('users.user',),
        ),
        migrations.AlterUniqueTogether(
            name='deviceuser',
            unique_together=set([('device_user_token', 'user')]),
        ),
    ]
