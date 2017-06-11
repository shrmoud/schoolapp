# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, timedelta

from django.db import migrations, models
from django.utils import timezone
from django.utils.timezone import localtime


def add_microseconds(apps, schema_editor):
    """
    Adds a microsecond at date
    """
    model = apps.get_model('scheduled_classes', 'Class')

    lessons = model.objects.all()

    for lesson in lessons:

        if lesson.class_start_date:
            #
            # adds a microsecond at current date
            lesson.class_start_date = lesson.class_start_date + timedelta(
                microseconds=1
            )
            lesson.save()
        else:
            #
            # if class_start_date is equal None
            # it is added current date
            now = timezone.now()
            lesson.class_start_date = now
            lesson.save()


class Migration(migrations.Migration):

    dependencies = [
        ('scheduled_classes', '0006_merge'),
    ]

    operations = [
        migrations.RunPython(add_microseconds)
    ]
