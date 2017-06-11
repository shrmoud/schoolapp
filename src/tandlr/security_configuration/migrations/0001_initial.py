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
            name='Permission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(unique=True, max_length=45)),
                ('description', models.TextField(max_length=100, null=True, blank=True)),
                ('status', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='PermissionRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('permission', models.ForeignKey(to='security_configuration.Permission')),
            ],
            options={
                'db_table': 'permission_role',
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(unique=True, max_length=45)),
                ('description', models.TextField(max_length=100, null=True, blank=True)),
                ('status', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'role',
            },
        ),
        migrations.CreateModel(
            name='RoleUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role', models.ForeignKey(to='security_configuration.Role')),
                ('user', models.ForeignKey(related_name='roles', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'role_user',
            },
        ),
        migrations.AddField(
            model_name='permissionrole',
            name='role',
            field=models.ForeignKey(related_name='permission', to='security_configuration.Role'),
        ),
        migrations.AlterUniqueTogether(
            name='roleuser',
            unique_together=set([('role', 'user')]),
        ),
        migrations.AlterUniqueTogether(
            name='permissionrole',
            unique_together=set([('permission', 'role')]),
        ),
    ]
