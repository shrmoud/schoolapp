# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Class',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('class_start_date', models.DateTimeField(null=True, blank=True)),
                ('class_time', models.TimeField(null=True, blank=True)),
                ('class_end_date', models.DateTimeField(null=True, blank=True)),
                ('class_detail', models.TextField(max_length=500, null=True, blank=True)),
                ('place_description', models.TextField(max_length=250, null=True, blank=True)),
            ],
            options={
                'db_table': 'class',
            },
        ),
        migrations.CreateModel(
            name='ClassStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=45)),
                ('description', models.CharField(max_length=100, null=True, blank=True)),
                ('status', models.BooleanField(default=True)),
                ('order', models.PositiveIntegerField(default=1, help_text='Defines the order how to will display the list class')),
            ],
            options={
                'db_table': 'class_status',
                'verbose_name_plural': 'class status',
            },
        ),
        migrations.CreateModel(
            name='RequestClassExtensionTime',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.TimeField()),
                ('accepted', models.BooleanField(default=False)),
                ('finished', models.BooleanField(default=False)),
                ('extension_time_end_date', models.DateTimeField(null=True)),
                ('class_request', models.ForeignKey(related_name='extensions_time_class', to='scheduled_classes.Class')),
            ],
            options={
                'db_table': 'request_class_extension_time',
            },
        ),
        migrations.CreateModel(
            name='Slot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('is_unique', models.BooleanField(default=False)),
                ('date', models.DateField(null=True, blank=True)),
                ('monday', models.BooleanField(default=False)),
                ('tuesday', models.BooleanField(default=False)),
                ('wednesday', models.BooleanField(default=False)),
                ('thursday', models.BooleanField(default=False)),
                ('friday', models.BooleanField(default=False)),
                ('saturday', models.BooleanField(default=False)),
                ('sunday', models.BooleanField(default=False)),
                ('teacher', models.ForeignKey(related_name='availability_slots', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=45)),
                ('description', models.CharField(max_length=100, null=True, blank=True)),
                ('status', models.BooleanField(default=True)),
                ('price_per_hour', models.DecimalField(default=Decimal('40.00'), max_digits=10, decimal_places=2)),
            ],
            options={
                'db_table': 'subject',
                'verbose_name': 'subject',
                'verbose_name_plural': 'subjects',
            },
        ),
        migrations.CreateModel(
            name='SubjectTeacher',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.BooleanField(default=True)),
                ('subject', models.ForeignKey(related_name='subjects', to='scheduled_classes.Subject')),
                ('teacher', models.ForeignKey(related_name='subject_teacher', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'subject_teacher',
                'verbose_name': 'teacher subject',
                'verbose_name_plural': 'teacher subjects',
            },
        ),
        migrations.AddField(
            model_name='class',
            name='class_status',
            field=models.ForeignKey(related_name='class_status', to='scheduled_classes.ClassStatus'),
        ),
        migrations.AddField(
            model_name='class',
            name='student',
            field=models.ForeignKey(related_name='class_student', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='class',
            name='subject',
            field=models.ForeignKey(related_name='class_subject', to='scheduled_classes.Subject'),
        ),
        migrations.AddField(
            model_name='class',
            name='teacher',
            field=models.ForeignKey(related_name='class_teacher', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='subjectteacher',
            unique_together=set([('teacher', 'subject')]),
        ),
    ]
