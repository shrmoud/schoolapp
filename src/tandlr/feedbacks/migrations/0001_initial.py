# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('scheduled_classes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('feedback', models.TextField(max_length=500)),
                ('feedback_status', models.BooleanField(default=False)),
                ('is_feedback_teacher', models.BooleanField(default=False, verbose_name='Is teacher feedback')),
                ('create_date', models.DateField(auto_now=True)),
                ('score', models.FloatField(default=0.0, null=True)),
                ('feedback_class', models.ForeignKey(related_name='feedbacks', to='scheduled_classes.Class')),
                ('feedback_from_user', models.ForeignKey(related_name='feedback_from_user', to=settings.AUTH_USER_MODEL)),
                ('feedback_to_user', models.ForeignKey(related_name='feedback_to_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'feedback',
            },
        ),
    ]
