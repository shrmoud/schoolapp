# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('catalogues', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MassNotification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='created date', null=True)),
                ('last_modified', models.DateTimeField(auto_now=True, verbose_name='last modified', null=True)),
                ('body', models.CharField(help_text='The message that will be displayed in the notificiation.', max_length=255, verbose_name='body')),
                ('delivery_date', models.DateTimeField(help_text='The date & time on which the notification will be sent.\nNote that setting a past date will cause the notification to be sent immediatelly.', verbose_name='delivery date')),
                ('state', models.IntegerField(default=100, help_text='Tells whether the notification was already sent or it is scheduled for sending in future.', verbose_name='state', choices=[(100, 'Scheduled'), (200, 'Delivered')])),
                ('celery_task_id', models.CharField(help_text='The id of the celery task that will actually send the notifications.', max_length=36, verbose_name='celery task id')),
                ('university', models.ForeignKey(related_name='notifications', blank=True, to='catalogues.University', help_text='The university whose users will be notified. Leave blank to notify all users of the platform.', null=True, verbose_name='university')),
            ],
            options={
                'verbose_name': 'mass notification',
                'verbose_name_plural': 'mass notifications',
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='created date', null=True)),
                ('last_modified', models.DateTimeField(auto_now=True, verbose_name='last modified', null=True)),
                ('target_id', models.PositiveIntegerField(help_text='The id of the object that the notification points to.', null=True, verbose_name='target id', blank=True)),
                ('target_action', models.CharField(help_text='The action triggered by the object that the notification points to.', max_length=20, verbose_name='target action')),
                ('body', models.CharField(help_text='The message that will be displayed in the notificiation.', max_length=255, verbose_name='body')),
                ('was_delivered', models.BooleanField(default=False, help_text='Tells whether this notification was delivered to the receiver via push notificationsi or not.', verbose_name='was delivered')),
                ('is_read', models.BooleanField(default=False, help_text='Tells whether this notification is already read by the receiver or not.', verbose_name='is read')),
                ('receiver', models.ForeignKey(related_name='notifications', verbose_name='receiver', to=settings.AUTH_USER_MODEL, help_text='The user who has to receive the notification.')),
                ('sender', models.ForeignKey(related_name='sent_notifications', blank=True, to=settings.AUTH_USER_MODEL, help_text='The user who sends the notification. Can be null if the notifications is originated by a system action.', null=True, verbose_name='sender')),
                ('target_type', models.ForeignKey(related_name='notifications', blank=True, to='contenttypes.ContentType', help_text='The ContentType of the object that the notification points to.', null=True, verbose_name='target type')),
            ],
            options={
                'verbose_name': 'notification',
                'verbose_name_plural': 'notifications',
            },
        ),
    ]
