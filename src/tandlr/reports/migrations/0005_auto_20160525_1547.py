# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0004_auto_20160525_1522'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='activitysession',
            options={'verbose_name': 'Session activity', 'verbose_name_plural': 'Sessions activity'},
        ),
        migrations.AlterModelOptions(
            name='newuser',
            options={'verbose_name': 'New user', 'verbose_name_plural': 'New users'},
        ),
        migrations.AlterModelOptions(
            name='notificationsent',
            options={'verbose_name': 'Notification sent', 'verbose_name_plural': 'Notifications sent'},
        ),
        migrations.AlterModelOptions(
            name='sessioncancelled',
            options={'verbose_name': 'Session canceled', 'verbose_name_plural': 'Sessions canceled'},
        ),
        migrations.AlterModelOptions(
            name='sessionregistered',
            options={'verbose_name': 'Session registered', 'verbose_name_plural': 'Sessions registered'},
        ),
        migrations.AlterModelOptions(
            name='sessionsale',
            options={'verbose_name': 'Session sale', 'verbose_name_plural': 'Sessions sale'},
        ),
        migrations.AlterModelOptions(
            name='topstudentuser',
            options={'verbose_name': 'Top student user', 'verbose_name_plural': 'Top students user'},
        ),
        migrations.AlterModelOptions(
            name='topteacheruser',
            options={'verbose_name': 'Top teacher user', 'verbose_name_plural': 'Top teachers user'},
        ),
    ]
